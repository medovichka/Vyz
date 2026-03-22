using System;
using System.Collections.Generic;
using System.Configuration;
using System.Windows.Forms;
using static System.Runtime.InteropServices.Marshalling.IIUnknownCacheStrategy;

namespace Lab2
{
    public partial class Form1 : Form
    {
        private DatabaseHelper dbHelper;
        private List<Organization> currentOrgs;

        public Form1()
        {
            InitializeComponent();
            dbHelper = new DatabaseHelper();
            dbHelper.InitializeDatabase();
            UpdateList();
            ToggleFields(); // Настраиваем видимость полей при старте
        }

        private void UpdateList()
        {
            listBoxOrgs.Items.Clear();
            currentOrgs = dbHelper.GetAllOrganizations();
            foreach (var org in currentOrgs)
            {
                listBoxOrgs.Items.Add($"{org.Id} | {org.Name} | ИНН: {org.Inn} | {org.GetType().Name}");
            }
        }

        // --- Обработчики кнопок CRUD ---

        private void btnAdd_Click(object sender, EventArgs e)
        {
            try
            {
                string name = txtName.Text;
                string inn = txtInn.Text;
                int emp = int.Parse(txtEmployees.Text);

                if (rbComOrg.Checked)
                {
                    string profit = txtProfit.Text;
                    string busType = txtBusinessType.Text;
                    ComOrg newOrg = new ComOrg(name, inn, emp, profit, busType);
                    dbHelper.AddOrganization(newOrg);
                }
                else
                {
                    string purpose = txtPurpose.Text;
                    string source = txtSource.Text;
                    NonComOrg newOrg = new NonComOrg(name, inn, emp, purpose, source);
                    dbHelper.AddOrganization(newOrg);
                }
                UpdateList();

                // Очистка полей после добавления
                txtName.Clear(); txtInn.Clear(); txtEmployees.Clear();
                txtProfit.Clear(); txtBusinessType.Clear(); txtPurpose.Clear(); txtSource.Clear();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка ввода данных: " + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnDelete_Click(object sender, EventArgs e)
        {
            if (listBoxOrgs.SelectedIndex != -1)
            {
                var selectedOrg = currentOrgs[listBoxOrgs.SelectedIndex];
                dbHelper.DeleteOrganization(selectedOrg.Id);
                UpdateList();
            }
            else
            {
                MessageBox.Show("Выберите организацию из списка для удаления.", "Внимание", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }
        private void btnUpdate_Click(object sender, EventArgs e)
        {
            listBoxOrgs.Items.Clear();
            var fresh = dbHelper.GetAllOrganizations();
            foreach (var f in fresh)
            {
                listBoxOrgs.Items.Add(f);
                UpdateList();
            }
        }
        private void UpdateListBoxSelection(object sender, EventArgs e)
        {
            button1.Text = "Выберите организацию";
            button2.Text = "Выберите организацию";
            info1.Text = "";
            info2.Text = "";
            info3.Text = "";
            info4.Text = "";
            info5.Text = "";
            button4.Enabled = false;
            info1.Enabled = false;
            info2.Enabled = false;
            info3.Enabled = false;
            info4.Enabled = false;
            info5.Enabled = false;


            if (listBoxOrgs.SelectedIndex != -1)
            {
                button4.Enabled = true;
                var selectedOrg = currentOrgs[listBoxOrgs.SelectedIndex];

                if (selectedOrg is ComOrg comOrg)
                {

                    // Действия для коммерческой организации
                    button1.Text = $"Расширение";
                    button2.Text = $"Распределить прибыль";
                    var xz = "Информация не доступна";

                    info1.Enabled = true;
                    info2.Enabled = true;
                    info1.Text = comOrg.Profit.ToString();
                    info2.Text = comOrg.BusinessType;
                    info3.Enabled = false;
                    info4.Enabled = false;
                    info5.Enabled = true;
                    info5.Text = comOrg.Name;

                }
                else if (selectedOrg is NonComOrg nonComOrg)
                {
                    button1.Text = $"Провести программу";
                    button2.Text = $"Сбросить цель";

                    info3.Enabled = true;
                    info4.Enabled = true;
                    info3.Text = nonComOrg.FoundingSource;
                    info4.Text = nonComOrg.Purpose;
                    info1.Enabled = false;
                    info2.Enabled = false;
                    info5.Enabled= true;
                    info5.Text = nonComOrg.Name;
                }
            }
        }



        // --- Обработчики методов классов ---

        private void btnReport_Click(object sender, EventArgs e)
        {
            if (listBoxOrgs.SelectedIndex != -1)
            {

                var selectedOrg = currentOrgs[listBoxOrgs.SelectedIndex];
                MessageBox.Show(selectedOrg.Report(), "Отчет", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void btnTaxes_Click(object sender, EventArgs e)
        {
            if (listBoxOrgs.SelectedIndex != -1)
            {
                var selectedOrg = currentOrgs[listBoxOrgs.SelectedIndex];
                MessageBox.Show($"Расчет налога: {selectedOrg.Taxes()} руб.", "Налоги", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        // --- UI Логика ---

        // Событие переключения радио-кнопки
        private void rbComOrg_CheckedChanged(object sender, EventArgs e)
        {
            ToggleFields();
        }

        // Метод для скрытия/показа специфичных текстовых полей
        private void ToggleFields()
        {
            bool isCom = rbComOrg.Checked;

            labelProfit.Visible = isCom;
            txtProfit.Visible = isCom;
            labelBusinessType.Visible = isCom;
            txtBusinessType.Visible = isCom;

            labelPurpose.Visible = !isCom;
            txtPurpose.Visible = !isCom;
            labelSource.Visible = !isCom;
            txtSource.Visible = !isCom;
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void btnUnique1(object sender, EventArgs e)
        {
            if (listBoxOrgs.SelectedIndex != -1)
            {
                var selectedOrg = currentOrgs[listBoxOrgs.SelectedIndex];
                if (selectedOrg is NonComOrg nonCom)
                {
                    MessageBox.Show($"Проведена программа:\n{nonCom.Program("Программа")}", "Некоммерческая организация",
                        MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                else if (selectedOrg is ComOrg comOrg)
                {
                    string Novoe = comOrg.ExpandBusiness();
                    string result = Novoe;
                    comOrg.Profit = Novoe;
                    dbHelper.UpdateOrganization(comOrg);
                    MessageBox.Show($"Бизнес расширен, вот результат: {result}", "Коммерческая организация",
                        MessageBoxButtons.OK, MessageBoxIcon.Information);
                    UpdateListBoxSelection(sender, e);

                }
            }
        }
        private void btnUnique2(object sender, EventArgs e)
        {
            if (listBoxOrgs.SelectedIndex != -1)
            {
                var selectedOrg = currentOrgs[listBoxOrgs.SelectedIndex];
                if (selectedOrg is NonComOrg nonCom)
                {
                    nonCom.Purpose = "Ничего";
                    UpdateListBoxSelection(sender, e);

                }
                else if (selectedOrg is ComOrg comOrg)
                {
                    string Novoe = comOrg.Distribute();
                    string result = Novoe;
                    comOrg.Profit = Novoe;
                    dbHelper.UpdateOrganization(comOrg);
                    MessageBox.Show($"Бюджет, который можно распределить: {result}", "Некоммерческая организация",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                    UpdateListBoxSelection(sender, e);
                }
            }
        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (listBoxOrgs.SelectedIndex != -1)
            {
                var selectedOrg = currentOrgs[listBoxOrgs.SelectedIndex];
                if (selectedOrg is NonComOrg nonCom)
                {
                    nonCom.Name = info5.Text;
                    nonCom.FoundingSource = info4.Text;
                    nonCom.Purpose = info3.Text;
                    dbHelper.UpdateOrganization(nonCom);
                    btnUpdate_Click(sender, e);
                }
                else if (selectedOrg is ComOrg comOrg)
                {
                    comOrg.Name = info5.Text;
                    comOrg.Profit = info1.Text;
                    comOrg.BusinessType = info2.Text;
                    dbHelper.UpdateOrganization(comOrg);
                    btnUpdate_Click(sender, e);
                }
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }
    }
}