from odoo import models, fields, api
from odoo.exceptions import UserError
import discord
import datetime

VEGAN_REACTIONS = {
    'Monday': ':green_apple:',   # or whatever you like
    'Tuesday': ':red_apple:',
    'Wednesday': ':pear:',
    'Thursday': ':tangerine:',
    'Friday': ':lemon:',
}

class LunchWeek(models.Model):
    _name = 'lunch.week'
    _description = 'Lunch Week'

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    poll_id = fields.Char(string="Poll ID", copy=False)
    soup_information = fields.Text(string="Soup")
    week_line_ids = fields.One2many(comodel_name='lunch.week.line', inverse_name='week_id', string="Week Lines", copy=True)
    week_start_date = fields.Date(string="Week Start Date")
    week_end_date = fields.Date(string="Week End Date")
    survey_length = fields.Integer(string="Survey Length (in days)", default=5, required=True)

    @api.depends('week_start_date', 'week_end_date')
    def _compute_name(self):
        for record in self:
            if record.week_start_date and record.week_end_date:
                record.name = '%(start_date)s To %(end_date)s' % { 'start_date':record.week_start_date, 'end_date':record.week_end_date }
            else:
                record.name = 'New Menu'

    @api.onchange('week_line_ids')
    def on_weekline_change(self):
        self.ensure_one()
        weeklines = self.week_line_ids.mapped('weekday')
        if len(weeklines) > len(set(weeklines)):
            raise UserError("The weekday lunch entries should be unique")

    def create_poll(self):
        self.ensure_one()
        # making the menu message
        menu_message_title = '@everyone\n# Lunch Menu %(name)s' % {'name' : self.name} 
        soup_message = '## Soup of the week: \n%(soup)s' % {'soup' : self.soup_information}
        vegan_message = "-# Want a vegan alternative? " + " | ".join(
        f"{VEGAN_REACTIONS[dict(line._fields['weekday'].selection).get(line.weekday)]} = {dict(line._fields['weekday'].selection).get(line.weekday)}"
        for line in self.week_line_ids
        )
        main_menu = ""
        for line in self.week_line_ids:
            weekday = dict(line._fields['weekday'].selection).get(line.weekday)
            allergens = ', '.join(line.allergen_ids.mapped('name'))
            main_menu += (
                f"## {line.emoji} {weekday} - {line.entree_name}\n"
                f"**{line.entree_description}**\n"
                f"-# **Allergens:** {allergens or 'None'}\n"
                f"-# **Vegan Alternatives:** {line.alternatives or 'None'}\n"
                "---\n"
            )
        full_message = f"{menu_message_title}\n\n{soup_message}\n\n{main_menu}{vegan_message}"
        poll = discord.Poll(question="Which days will you eat lunch?", duration=datetime.timedelta(days=self.survey_length), multiple=True)
        for line in self.week_line_ids:
            poll = poll.add_answer(text=dict(line._fields['weekday'].selection).get(line.weekday))

        self.env['snack.bot'].create_poll(self, full_message, poll)
        return True

    def read_poll_results(self):
        self.ensure_one()
        self.env['snack.bot'].read_poll_results(self)
        return True



class LunchWeekLine(models.Model):
    _name = 'lunch.week.line'
    _description = 'Lunch Week Lines'
    _order = 'weekday ASC'

    weekday = fields.Selection([
        ('1mon', 'Monday'),
        ('2tue', 'Tuesday'),
        ('3wed', 'Wednesday'),
        ('4thu', 'Thursday'),
        ('5fri', 'Friday'),
    ], string="Weekday", required=True)
    week_id = fields.Many2one(comodel_name='lunch.week', string="Week")
    entree_name = fields.Char(string="Entree Name")
    entree_description = fields.Text(string="Entree Description")
    allergen_ids = fields.Many2many(string="Allergen Information", comodel_name='lunch.allergen')
    alternatives = fields.Text(string="Vegan/Vegetarian Alternatives")
    respondents = fields.Integer(string="Total Respondents", copy=False)
    vegan_count = fields.Integer(string="Vegan Respondents", copy=False)
    non_vegan_count = fields.Integer(string="Non-Vegan Respondents", copy=False)
    total_made = fields.Integer(string="Entreees Made", copy=False)
    emoji = fields.Char(string="Emoji", default='🍽️')

