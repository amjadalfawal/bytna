/** @odoo-module **/
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { patch } from 'web.utils';

patch(BarcodeModel.prototype, 'stock_barcode_mrp_subcontracting', {

    async _processBarcode(barcode) {
        let new_flag = false; 

        console.log('======new=====');
        console.log(barcode);
        let firstTwoChars = str.slice(0, 2);
        console.log(firstTwoChars); // Co
        const data = this._super(...arguments);
    }

});
