# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    facturae_receiver_contract_reference = fields.Char()
    facturae_receiver_contract_date = fields.Date()
    facturae_receiver_transaction_reference = fields.Char()
    facturae_receiver_transaction_date = fields.Date()
    facturae_issuer_contract_reference = fields.Char()
    facturae_issuer_contract_date = fields.Date()
    facturae_issuer_transaction_reference = fields.Char()
    facturae_issuer_transaction_date = fields.Date()
    facturae_file_reference = fields.Char()
    facturae_file_date = fields.Date()
    facturae_start_date = fields.Date()
    facturae_end_date = fields.Date()
    facturae_transaction_date = fields.Date()

    @api.constrains("facturae_start_date", "facturae_end_date")
    def _check_facturae_date(self):
        for record in self:
            if bool(record.facturae_start_date) != bool(record.facturae_end_date):
                raise ValidationError(
                    _(
                        "Facturae start and end dates are both required if one of "
                        "them is filled"
                    )
                )
            if (
                record.facturae_start_date
                and record.facturae_start_date > record.facturae_end_date
            ):
                raise ValidationError(_("Start date cannot be later than end date"))

    def button_edit_facturae_fields(self):
        self.ensure_one()
        view = self.env.ref("l10n_es_facturae.view_facturae_fields")
        return {
            "name": _("Facturae Configuration"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": self._name,
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": self.env.context,
        }

    def _get_subtotal_without_discount(self):
        self.ensure_one()
        if self.display_type != "product":
            return 0
        subtotal = self.quantity * self.price_unit
        if self.tax_ids:
            taxes_res = self.tax_ids.compute_all(
                self.price_unit,
                quantity=self.quantity,
                currency=self.currency_id,
                product=self.product_id,
                partner=self.partner_id,
                is_refund=self.is_refund,
            )
            return taxes_res["total_excluded"]
        else:
            return subtotal

    def _facturae_get_price_unit(self):
        # Se añade esta funcionalidad para el caso en el cual algún impuesto de la
        # factura sea con el precio incluido. De esta forma se obtiene siemrpe el
        # precio sin impuestos. Como es el precio unitario lo que se calcula, no se
        # deben tener en cuenta los descuentos que pueda tener la factura
        self.ensure_one()
        if any(tax.price_include for tax in self.tax_ids):
            taxes_res = self.tax_ids.compute_all(
                self.price_unit,
                quantity=1.0,
                currency=self.currency_id,
                product=self.product_id,
                partner=self.partner_id,
                is_refund=self.is_refund,
            )
            return taxes_res["total_excluded"]
        return self.price_unit
