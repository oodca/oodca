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

import time
from datetime import datetime
from datetime import timedelta
import pytz
import base64
from io import StringIO

# noinspection PyUnresolvedReferences
from odoo.modules import get_module_resource

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
        'Barcode', copy=False, oldname='ean13',
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

            if barcode_count.isdigit():
                no_producto = int(barcode_count)
        else:
            barcode_count = 0
            for product in PRODUCTS:
                if product.barcode:
                    barcode_count = barcode_count + 1

            no_producto = barcode_count + 1

            barcode_count = str(no_producto)


        # ----------------------------------------
        # SE DETERMINA EL formato DEL no_producto
        # ----------------------------------------
        if barcode_count.isdigit():
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
        if barcode_count.isdigit():
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

    # --------------------------------------------------------------
    # API:      ACTUALIZAR_TODOS
    # function: actualizar_ruc(self)
    # ------------------------------
    @api.multi
    def actualizar_imagenes(self):

        finish_at = time.time() + 119

        utc_now = datetime.today()
        pst_now = utc_now.astimezone(pytz.timezone("America/Guayaquil"))
        pst_now_str = pst_now.strftime("%Y-%m-%d")
        # pst_now_obj = datetime.strptime(pst_now_str, '%Y-%m-%d').date()

        ahora = pst_now.date()
        hace_30_dias = ahora - timedelta(days=1)

        PRODUCTOS = self.env['product.product'].search([])
        total_contactos = len(PRODUCTOS)
        total_avance = 0
        total_contactos_sin_actualizar = 0

        for producto in PRODUCTOS:

                temporizador = time.time()
                logging.info('ACTUALIZANDO ID: ' + str(producto.id) + ' / ' + str(producto.name) + ' / ' + str(
                    '{:.1f}'.format(finish_at - temporizador)))

                producto_nombre = producto.name
                # -------------------------------------------------------------------------------
                # RECUPERA DEL DISCO EL ARCHIVO PNG CON LA IMAGEN PREDEFINIDA DE LA SECCION CIIU
                # -------------------------------------------------------------------------------
                if not producto.image_medium:

                    codigo_retencion = '000'

                    nombre_producto = producto.name
                    impuestos = producto.taxes_id

                    for tax in producto.supplier_taxes_id:
                        # ------------------------------------
                        # codigo_tabla_19 TABLA 19 DEFINICION
                        # codigo_tabla_20 TABLA 20 DEFINICION
                        # ------------------------------------
                        #             '__3__3 _2_______81 ___4
                        #              RIR 10 ssHonorProC 303
                        #              RIR 08 ssComisIntC 304A
                        #              RIV100 bsComIVA12C 731
                        #              RIV 00 bsComIVA00C 002
                        #              RIV 00 bsComNoSujC 002
                        #              -----------------------
                        #              01234567890123456789012
                        # ------------------------------------
                        impuesto = tax.name
                        nombre_impuesto = impuesto[0:3]

                        if nombre_impuesto == 'RIR':
                            codigo_retencion = impuesto[19:23]

                    # logging.info('IMPUESTO: ' + nombre_impuesto + ' ' + codigo_retencion)

                    nombre_archivo_png = get_module_resource(
                        'l10n_ec_invoice',
                        'static/src/img',
                        codigo_retencion + '.png'
                    )

                    # logging.info('OPEN FILE: ' + nombre_archivo_png )

                    try:
                        image = open(nombre_archivo_png, "rb")
                        image_read = image.read()

                        # logging.info('LECTURA (Ok)')

                        image_64_encode = base64.encodebytes(image_read)
                        image_64_bytes = image_64_encode.decode(encoding="utf-8")

                        # logging.info('ARCHIVO: ' + nombre_archivo_png + ' (Ok)')

                    except Exception as error_message:
                        logging.info(str(error_message))

                        # logging.info('OPEN FILE: ' + '000.png')

                        image = open('000.png', "rb")
                        image_read = image.read()

                        # logging.info('LECTURA (Ok)')

                        image_64_encode = base64.encodebytes(image_read)
                        image_64_bytes = image_64_encode.decode(encoding="utf-8")

                    if not producto.image_variant:
                        # logging.info('PREVIA: ' + nombre_producto)

                        # noinspection PyAttributeOutsideInit
                        producto.product_tmpl_id.image = image_64_bytes
                        # producto.image_variant = image_64_bytes

                        # logging.info('IMAGEN: ' + nombre_producto)


                if time.time() > finish_at:
                    # ---------------------------------------------------------------------------
                    # MESSAGE_BOX CODE: USAR PARA MENSAJES INFORMATIVOS QUE NO DETENGAN PROCESOS
                    # SOLO PARA @api.multi
                    # ---------------------------------------------------------------------------
                    title = "INFORMACION:"
                    message_1 = 'SE ACTUALIZARON ' + str(total_avance) + ' DE ' + str(
                        total_contactos_sin_actualizar) + ' IMAGENES. '
                    message_2 = 'CULMINE EL PROCESO DE ACTUALIZACION PRESIONANDO VARIAS VECES [ACTUALIZAR TODO]'
                    message = message_1 + message_2
                    view = self.env.ref('l10n_ec_partner.message_box_form')
                    # view_id = view and view.id or False
                    context = dict(self._context or {})
                    context['message'] = message
                    return {'name': title,
                            'type': 'ir.actions.act_window',
                            'res_model': 'message_box',
                            'view_mode': 'form',
                            'view_type': 'form',
                            'view_id': view.id,
                            'target': 'new',
                            'context': context,
                            }
        # ---------------------------------------------------------------------------
        # MESSAGE_BOX CODE: USAR PARA MENSAJES INFORMATIVOS QUE NO DETENGAN PROCESOS
        # SOLO PARA @api.multi
        # ---------------------------------------------------------------------------
        title = "INFORMACION:"
        message = 'TODOS LOS CONTACTOS SE ENCUENTRAN ACTUALIZADOS.'
        view = self.env.ref('l10n_ec_partner.message_box_form')
        # view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = message
        return {'name': title,
                'type': 'ir.actions.act_window',
                'res_model': 'message_box',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view.id,
                'target': 'new',
                'context': context,
                }
