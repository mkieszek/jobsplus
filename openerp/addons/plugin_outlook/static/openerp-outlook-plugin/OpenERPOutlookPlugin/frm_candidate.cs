/*
    OpenERP, Open Source Business Applications
    Copyright (c) 2011 OpenERP S.A. <http://openerp.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


using System;
using System.Collections;
using System.Windows.Forms;
using OpenERPClient;
using System.ComponentModel;
namespace OpenERPOutlookPlugin
{

    public partial class frm_candidate : Form
    {

        public frm_candidate()
        {
            InitializeComponent();
            txtEmail.Text = Tools.MailItems()[0].SenderEmailAddress;
        }

        public frm_candidate(string contact_name, string email_id)
        {
            InitializeComponent();
            txt_candidate.Text = contact_name;
            txtPhone.Text = email_id;
            txtEmail.Text = Tools.MailItems()[0].SenderEmailAddress;
        }
      
        private void btncancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void btnCreateCandidate_Click(object sender, EventArgs e)
        {
            try
            {
                Cache.OpenERPOutlookPlugin.CreateCandidateRecord(Tools.MailItems()[0], (cmbDeal.SelectedValue as Record).id, txt_candidate.Text, txtPhone.Text, txtEmail.Text);
                this.Close();
            }
            catch (Exception ex)
            {
                Connect.handleException(ex);
            }
        }


        private void frm_candidate_Load(object sender, EventArgs e)
        {
            //Record[] deal_list =

            if (Tools.MailItems().Length != 1)
            {
                throw new Exception("You have to choose exactly one mail message");
            }
            BindingList < Record > list = new BindingList<Record>(Cache.OpenERPOutlookPlugin.GetDealList());

            cmbDeal.DataSource = list;
            
            /*foreach (Record deal in deal_list)
            {
                cmbDeal.Items.Add(deal.name);
            }*/
        }

    }
}
