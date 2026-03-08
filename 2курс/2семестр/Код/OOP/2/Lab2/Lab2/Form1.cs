using System;
using System.Collections.Generic;
using System.Windows.Forms;

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
                    int profit = int.Parse(txtProfit.Text);
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
    }
}