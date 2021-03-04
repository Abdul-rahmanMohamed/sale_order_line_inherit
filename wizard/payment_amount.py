# -*- coding: utf-8 -*-
from odoo import fields, models


class PaymentAmountWizard(models.TransientModel):
    _name = 'installment_amount_wizard'

    date = fields.Date(related='name.date', required=True)
    name = fields.Many2one('installment.installment', string="Name")
    amount = fields.Float(required=True, positive=True)
    journal = fields.Many2one(related='name.journal', string="Journal", required=True)
    reference = fields.Char(related='name.reference', string="Reference")

    def post_payment(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        accessmodel = self.env['installment.installment'].browse(active_ids)
        journal = self.journal
        payment_methods = journal.outbound_payment_method_ids if self.amount < 0 else journal.inbound_payment_method_ids

        # Create payment and post it
        payment = self.env['account.payment'].create({
            'payment_date': self.date,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': accessmodel.customer.id,
            'amount': accessmodel.amount,
            'journal_id': self.journal.id,
            'payment_method_id': payment_methods.id,
        })
        if self.amount == accessmodel.amount:
            accessmodel.state = 'paid'
        else:
            accessmodel.satate = 'open'
