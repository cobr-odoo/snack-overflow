from odoo import models, fields, api


class LunchAllergen(models.Model):
    _name = 'lunch.allergen'
    _description = "Allergen"

    name = fields.Char(string="Allergen Name")