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
using outlook = Microsoft.Office.Interop.Outlook;
namespace OpenERPOutlookPlugin
{

    

    public partial class frm_candidate_multi : Form
    {
        Microsoft.Office.Interop.Outlook.MailItem[] items;

        BindingList<Candidate> list = new BindingList<Candidate>();

        public frm_candidate_multi()
        {
            InitializeComponent();
            items = Tools.MailItems();

            foreach (var mail in items)
            {
                Candidate c = new Candidate();
                c.Email = mail.SenderEmailAddress;
                c.Title = mail.Subject;
                
                list.Add(c);
            }

            gvCandidate.DataSource = list;

            txtStatus.Text = String.Format("Sent {0} of {1}", 0, list.Count);
        }

        public frm_candidate_multi(string contact_name, string email_id)
        {
            InitializeComponent();
            

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
                int i = 0;
                foreach (var mail in items)
                {
                    try
                    {
                        Cache.OpenERPOutlookPlugin.CreateCandidateRecord(mail, 0, mail.SenderEmailAddress, "", mail.SenderEmailAddress, txtPosition.Text, false);

                        list[i].Status = "Wys³ano";
                        list[i].SentDate = DateTime.Now;
                    }
                    catch (Exception ex)
                    {
                        list[i].Status = "B³¹d: " + ex.Message;
                    }
                    
                    gvCandidate.Refresh();
                                        
                    i++;

                    txtStatus.Text = String.Format("Wys³ano {0} z {1}", i, list.Count);

                    txtStatus.Refresh();
                }

                if (MessageBox.Show(String.Format("Wys³ano {0} z {1}\n Czy chcesz zamkn¹æ okno importu?", i, list.Count), "Zakoñczony import kandydatów", MessageBoxButtons.OKCancel, MessageBoxIcon.Information) == System.Windows.Forms.DialogResult.OK)
                {
                    this.Close();
                }
            }
            catch (Exception ex)
            {
                Connect.handleException(ex);
            }
        }


        private void frm_candidate_multi_Load(object sender, EventArgs e)
        {
            //Record[] deal_list =

            /*foreach (Record deal in deal_list)
            {
                cmbDeal.Items.Add(deal.name);
            }*/
        }

    }

    public class Candidate
    {
        private String email;
        private String title;
        private String status;
        private DateTime sentDate;
        
        public String Title
        {
            get { return title; }
            set { title = value; }
        }

        public String Email
        {
            get { return email; }
            set { email = value; }
        }

        public String Status
        {
            get { return status; }
            set { status = value; }

        }
        public DateTime SentDate
        {
            get
            {
                return sentDate;
            }
            set
            {
                sentDate = value;
            }
        }
    }
}
