from odoo import models, fields
import discord
from collections import defaultdict
SWAPPED_VEGAN_REACTIONS = {
    ':green_apple:': 'Monday',
    ':red_apple:': 'Tuesday',
    ':pear:': 'Wednesday',
    ':tangerine:': 'Thursday',
    ':lemon:': 'Friday',
}

VEGAN_REACTIONS = {
    'Monday': ':green_apple:',   # or whatever you like
    'Tuesday': ':red_apple:',
    'Wednesday': ':pear:',
    'Thursday': ':tangerine:',
    'Friday': ':lemon:',
}

EMOJI_REACTIONS = {
    'Monday': '🍏',
    'Tuesday': '🍎',
    'Wednesday': '🍐',
    'Thursday': '🍊',
    'Friday': '🍋',
}



class SnackBot(models.Model):
    _name = 'snack.bot'
    _description = 'Snack Bot'

    name = fields.Char(string="Name")
    client_token = fields.Char(string="Client Token")
    client_secret = fields.Char(string="Client Secret")

    server_id = fields.Char(string="Server ID")
    channel_id = fields.Char(string="Channel ID")
    
    def create_poll(self, week, message, poll):
        bot_id = self.env.ref('snack.snack_bot')
        
        intents = discord.Intents.default()
        intents.message_content = True

        client = NonInteractiveBot(self, self.send_odoo_poll, week, message=message, poll=poll, intents=intents)

        client.run(bot_id.client_secret)
        return True
    
    async def send_odoo_poll(self, client):
        bot_id = self.env.ref('snack.snack_bot')
        guild = client.get_guild(int(bot_id.server_id))
        channel = guild.get_channel(int(bot_id.channel_id))
        await channel.send(client.message)
        poll = await channel.send(poll=client.poll)
        for emoji in EMOJI_REACTIONS.values():
            await poll.add_reaction(emoji)
        client.week.poll_id = poll.id
    
    def read_poll_results(self, week):
        bot_id = self.env.ref('snack.snack_bot')
        
        intents = discord.Intents.default()
        intents.message_content = True

        client = NonInteractiveBot(self, self.read_odoo_poll, week, poll=week.poll_id, intents=intents)

        client.run(bot_id.client_secret)

    async def read_odoo_poll(self, client):
        bot_id = self.env.ref('snack.snack_bot')
        guild = client.get_guild(int(bot_id.server_id))
        channel = guild.get_channel(int(bot_id.channel_id))
        msg = await channel.fetch_message(client.poll)
        poll = msg.poll
        answers = poll.answers
        line_by_weekday = {dict(line._fields['weekday'].selection).get(line.weekday): line for line in client.week.week_line_ids}
        react_count = defaultdict(int)
        for reaction in msg.reactions:
            react_count[reaction.emoji] = reaction.count
        for answer in answers:
            line = line_by_weekday.get(answer.text)
            line.respondents = answer.vote_count
            line.vegan_count = react_count[EMOJI_REACTIONS[answer.text]] - 1
            line.non_vegan_count = line.respondents - line.vegan_count


class NonInteractiveBot(discord.Client):

    def __init__(self, odoo_client, callback, week=False, **kwargs):
        super().__init__(**kwargs)
        self.odoo_client = odoo_client
        self.callback = callback
        self.week = week
        self.poll = kwargs.get('poll')
        self.message = kwargs.get('message')

    async def on_ready(self):
        await self.wait_until_ready()
        await self.callback(self)
        await self.close()
