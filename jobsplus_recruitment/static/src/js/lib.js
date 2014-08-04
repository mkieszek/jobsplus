openerp.resource = function (openerp)
{   
    openerp.web.form.widgets.add('jp_binary', 'openerp.resource.Mywidget');
    openerp.resource.Mywidget = openerp.web.form.FieldChar.extend(
        {
        template : "jp_binary",
        init: function (view, code) {
            this._super(view, code);
            console.log('loading...');
        }
    });
}