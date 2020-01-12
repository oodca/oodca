# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# Ecuador Invoice
# Localización para Odoo V12
# Por: Oodca Sociedad Anónima © <2019> <José Enríquez>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# -------------------------------------------------------------------------

# ---------------------------
# Notes:    LIBRERIAS PYTHON
# ---------------------------

# noinspection PyUnresolvedReferences
from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------
#   O   OOOOO OOOOO OOOOO O   O O   O OOOOO     OOO  O   O O   O OOOOO  OOO  OOOOO OOOOO
#  O O  O     O     O   O O   O OO  O   O        O   OO  O O   O O   O   O   O     O
# O   O O     O     O   O O   O O O O   O        O   O O O O   O O   O   O   O     OOO
# OOOOO O     O     O   O O   O O  OO   O        O   O  OO  O O  O   O   O   O     O
# O   O OOOOO OOOOO OOOOO OOOOO O   O   O       OOO  O   O   O   OOOOO  OOO  OOOOO OOOOO
# ----------------------------------------------------------------------------------------------------------------------
class ProductProduct(models.Model):
    _inherit = 'product.product'

    # ----------------------------------
    # MODIFICACION DE CAMPOS EXISTENTES
    # ----------------------------------
    barcode = fields.Char(
        'Barcode', copy=False, oldname='ean13', readonly=True,
        help="International Article Number used for product identification.")

    # --------------------------
    # DEFINICION DE CAMPOS BOOL
    # --------------------------
    bool_barcode = fields.Boolean(
        string='Modificar Cód.Barras',
        default=False,
        copy=False,
        help='Señale para acceder y modificar el Código de Barras'
    )

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––– @api ––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    @api.onchange('default_code', 'supplier_taxes_id')
    def _onchange_for_barcode(self):
        # ------------------------------------------------------------------------
        # DETERMINA EL CODIGO DE BARRAS PARA EL PRODUCTO CREADO O MODIFICADO
        # ------------------------------------------------------------------------

        formato = {}

        PRODUCTS = self.env['product.product'].search([])

        # --------------------------------------------------------------------------
        # SE DETERMINA EL no_producto DEL ITEM QUE SE ESTA INGRESANDO O MODIFICANDO
        # --------------------------------------------------------------------------
        if self.barcode:
            barcode_count = self.barcode.split('-')[0]

            no_producto = int(barcode_count)
        else:
            barcode_count = 0
            for product in PRODUCTS:
                if product.barcode:
                    barcode_count = barcode_count + 1

            no_producto = barcode_count + 1

        # ----------------------------------------
        # SE DETERMINA EL formato DEL no_producto
        # ----------------------------------------
        if no_producto <= 999:
            formato = '%03i'
        elif no_producto <= 9999:
            formato = '%04i'
        elif no_producto <= 99999:
            formato = '%05i'

        product_ids = self.supplier_taxes_id

        codigo = str(formato % 0)

        for product_id in product_ids:
            tipo_impuesto = product_id.name[0:3]
            if tipo_impuesto == 'RIR':
                codigo = product_id.name[19:22]

        # -----------------------------------
        # SE DETERMINA EL barcode PERTINENTE
        # -----------------------------------
        if self.default_code:
            self.barcode = str(formato % no_producto) + '-' + self.default_code + '-' + str(codigo)
            vals = {
                'barcode': self.barcode
            }
            producto = self.env['product.product'].search([('id', '=', self._origin.id)])
            producto.write(vals)

        return

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––– @api ––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # ---------------------------------------------------------------------------
        # SE MANTIENE LA ESTRUCTURA DEL PROGRAMA DE ODOO:
        # tipo:     @api.multi
        #           @api.returns
        # FUNCION:  def action_invoice_open(self)
        # ORIGEN:   /addons/product/models/product.py
        # CLASS:    ProductProduct(models.Model):
        # ---------------------------------------------------------------------------
        # TDE FIXME: clean context / variant brol
        if default is None:
            default = {}
        if self._context.get('variant'):
            # if we copy a variant or create one, we keep the same template
            default['product_tmpl_id'] = self.product_tmpl_id.id
        elif 'name' not in default:
            # ------------------------------------------------------------------------
            # SE AÑADE LA PALABRA (COPIA) A LOS ELEMENTOS QUE DEBEN SER CAMBIADOS POR
            # EL USUARIO AL CREAR UNA COPIA
            # ------------------------------------------------------------------------
            default['name'] = self.name + '(COPIA)'
            default['default_code'] = self.default_code + '(COPIA)'

        return super(ProductProduct, self).copy(default=default)
