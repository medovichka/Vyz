namespace Lab2
{
    partial class Form1
    {
        /// <summary>
        /// Обязательная переменная конструктора.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Освободить все используемые ресурсы.
        /// </summary>
        /// <param name="disposing">истинно, если управляемый ресурс должен быть удален; иначе ложно.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Код, автоматически созданный конструктором форм Windows

        /// <summary>
        /// Требуемый метод для поддержки конструктора — не изменяйте 
        /// содержимое этого метода с помощью редактора кода.
        /// </summary>
        private void InitializeComponent()
        {
            this.listBoxOrgs = new System.Windows.Forms.ListBox();
            this.groupBoxData = new System.Windows.Forms.GroupBox();
            this.labelSource = new System.Windows.Forms.Label();
            this.txtSource = new System.Windows.Forms.TextBox();
            this.labelPurpose = new System.Windows.Forms.Label();
            this.txtPurpose = new System.Windows.Forms.TextBox();
            this.labelBusinessType = new System.Windows.Forms.Label();
            this.txtBusinessType = new System.Windows.Forms.TextBox();
            this.labelProfit = new System.Windows.Forms.Label();
            this.txtProfit = new System.Windows.Forms.TextBox();
            this.rbNonComOrg = new System.Windows.Forms.RadioButton();
            this.rbComOrg = new System.Windows.Forms.RadioButton();
            this.labelEmployees = new System.Windows.Forms.Label();
            this.txtEmployees = new System.Windows.Forms.TextBox();
            this.labelInn = new System.Windows.Forms.Label();
            this.txtInn = new System.Windows.Forms.TextBox();
            this.labelName = new System.Windows.Forms.Label();
            this.txtName = new System.Windows.Forms.TextBox();
            this.groupBoxCRUD = new System.Windows.Forms.GroupBox();
            this.btnDelete = new System.Windows.Forms.Button();
            this.btnAdd = new System.Windows.Forms.Button();
            this.groupBoxMethods = new System.Windows.Forms.GroupBox();
            this.btnTaxes = new System.Windows.Forms.Button();
            this.btnReport = new System.Windows.Forms.Button();
            this.groupBoxData.SuspendLayout();
            this.groupBoxCRUD.SuspendLayout();
            this.groupBoxMethods.SuspendLayout();
            this.SuspendLayout();
            // 
            // listBoxOrgs
            // 
            this.listBoxOrgs.FormattingEnabled = true;
            this.listBoxOrgs.ItemHeight = 20;
            this.listBoxOrgs.Location = new System.Drawing.Point(12, 12);
            this.listBoxOrgs.Name = "listBoxOrgs";
            this.listBoxOrgs.Size = new System.Drawing.Size(350, 504);
            this.listBoxOrgs.TabIndex = 0;
            // 
            // groupBoxData
            // 
            this.groupBoxData.Controls.Add(this.labelSource);
            this.groupBoxData.Controls.Add(this.txtSource);
            this.groupBoxData.Controls.Add(this.labelPurpose);
            this.groupBoxData.Controls.Add(this.txtPurpose);
            this.groupBoxData.Controls.Add(this.labelBusinessType);
            this.groupBoxData.Controls.Add(this.txtBusinessType);
            this.groupBoxData.Controls.Add(this.labelProfit);
            this.groupBoxData.Controls.Add(this.txtProfit);
            this.groupBoxData.Controls.Add(this.rbNonComOrg);
            this.groupBoxData.Controls.Add(this.rbComOrg);
            this.groupBoxData.Controls.Add(this.labelEmployees);
            this.groupBoxData.Controls.Add(this.txtEmployees);
            this.groupBoxData.Controls.Add(this.labelInn);
            this.groupBoxData.Controls.Add(this.txtInn);
            this.groupBoxData.Controls.Add(this.labelName);
            this.groupBoxData.Controls.Add(this.txtName);
            this.groupBoxData.Location = new System.Drawing.Point(380, 12);
            this.groupBoxData.Name = "groupBoxData";
            this.groupBoxData.Size = new System.Drawing.Size(440, 330);
            this.groupBoxData.TabIndex = 1;
            this.groupBoxData.TabStop = false;
            this.groupBoxData.Text = "Данные организации";
            // 
            // labelSource
            // 
            this.labelSource.AutoSize = true;
            this.labelSource.Location = new System.Drawing.Point(15, 290);
            this.labelSource.Name = "labelSource";
            this.labelSource.Size = new System.Drawing.Size(86, 20);
            this.labelSource.TabIndex = 15;
            this.labelSource.Text = "Источник:";
            // 
            // txtSource
            // 
            this.txtSource.Location = new System.Drawing.Point(130, 287);
            this.txtSource.Name = "txtSource";
            this.txtSource.Size = new System.Drawing.Size(290, 27);
            this.txtSource.TabIndex = 14;
            // 
            // labelPurpose
            // 
            this.labelPurpose.AutoSize = true;
            this.labelPurpose.Location = new System.Drawing.Point(15, 257);
            this.labelPurpose.Name = "labelPurpose";
            this.labelPurpose.Size = new System.Drawing.Size(47, 20);
            this.labelPurpose.TabIndex = 13;
            this.labelPurpose.Text = "Цель:";
            // 
            // txtPurpose
            // 
            this.txtPurpose.Location = new System.Drawing.Point(130, 254);
            this.txtPurpose.Name = "txtPurpose";
            this.txtPurpose.Size = new System.Drawing.Size(290, 27);
            this.txtPurpose.TabIndex = 12;
            // 
            // labelBusinessType
            // 
            this.labelBusinessType.AutoSize = true;
            this.labelBusinessType.Location = new System.Drawing.Point(15, 224);
            this.labelBusinessType.Name = "labelBusinessType";
            this.labelBusinessType.Size = new System.Drawing.Size(95, 20);
            this.labelBusinessType.TabIndex = 11;
            this.labelBusinessType.Text = "Тип бизнеса:";
            // 
            // txtBusinessType
            // 
            this.txtBusinessType.Location = new System.Drawing.Point(130, 221);
            this.txtBusinessType.Name = "txtBusinessType";
            this.txtBusinessType.Size = new System.Drawing.Size(290, 27);
            this.txtBusinessType.TabIndex = 10;
            // 
            // labelProfit
            // 
            this.labelProfit.AutoSize = true;
            this.labelProfit.Location = new System.Drawing.Point(15, 191);
            this.labelProfit.Name = "labelProfit";
            this.labelProfit.Size = new System.Drawing.Size(76, 20);
            this.labelProfit.TabIndex = 9;
            this.labelProfit.Text = "Прибыль:";
            // 
            // txtProfit
            // 
            this.txtProfit.Location = new System.Drawing.Point(130, 188);
            this.txtProfit.Name = "txtProfit";
            this.txtProfit.Size = new System.Drawing.Size(290, 27);
            this.txtProfit.TabIndex = 8;
            // 
            // rbNonComOrg
            // 
            this.rbNonComOrg.AutoSize = true;
            this.rbNonComOrg.Location = new System.Drawing.Point(230, 140);
            this.rbNonComOrg.Name = "rbNonComOrg";
            this.rbNonComOrg.Size = new System.Drawing.Size(148, 24);
            this.rbNonComOrg.TabIndex = 7;
            this.rbNonComOrg.Text = "Некоммерческая";
            this.rbNonComOrg.UseVisualStyleBackColor = true;
            // 
            // rbComOrg
            // 
            this.rbComOrg.AutoSize = true;
            this.rbComOrg.Checked = true;
            this.rbComOrg.Location = new System.Drawing.Point(70, 140);
            this.rbComOrg.Name = "rbComOrg";
            this.rbComOrg.Size = new System.Drawing.Size(131, 24);
            this.rbComOrg.TabIndex = 6;
            this.rbComOrg.TabStop = true;
            this.rbComOrg.Text = "Коммерческая";
            this.rbComOrg.UseVisualStyleBackColor = true;
            this.rbComOrg.CheckedChanged += new System.EventHandler(this.rbComOrg_CheckedChanged);
            // 
            // labelEmployees
            // 
            this.labelEmployees.AutoSize = true;
            this.labelEmployees.Location = new System.Drawing.Point(15, 103);
            this.labelEmployees.Name = "labelEmployees";
            this.labelEmployees.Size = new System.Drawing.Size(95, 20);
            this.labelEmployees.TabIndex = 5;
            this.labelEmployees.Text = "Сотрудники:";
            // 
            // txtEmployees
            // 
            this.txtEmployees.Location = new System.Drawing.Point(130, 100);
            this.txtEmployees.Name = "txtEmployees";
            this.txtEmployees.Size = new System.Drawing.Size(290, 27);
            this.txtEmployees.TabIndex = 4;
            // 
            // labelInn
            // 
            this.labelInn.AutoSize = true;
            this.labelInn.Location = new System.Drawing.Point(15, 70);
            this.labelInn.Name = "labelInn";
            this.labelInn.Size = new System.Drawing.Size(45, 20);
            this.labelInn.TabIndex = 3;
            this.labelInn.Text = "ИНН:";
            // 
            // txtInn
            // 
            this.txtInn.Location = new System.Drawing.Point(130, 67);
            this.txtInn.Name = "txtInn";
            this.txtInn.Size = new System.Drawing.Size(290, 27);
            this.txtInn.TabIndex = 2;
            // 
            // labelName
            // 
            this.labelName.AutoSize = true;
            this.labelName.Location = new System.Drawing.Point(15, 37);
            this.labelName.Name = "labelName";
            this.labelName.Size = new System.Drawing.Size(80, 20);
            this.labelName.TabIndex = 1;
            this.labelName.Text = "Название:";
            // 
            // txtName
            // 
            this.txtName.Location = new System.Drawing.Point(130, 34);
            this.txtName.Name = "txtName";
            this.txtName.Size = new System.Drawing.Size(290, 27);
            this.txtName.TabIndex = 0;
            // 
            // groupBoxCRUD
            // 
            this.groupBoxCRUD.Controls.Add(this.btnDelete);
            this.groupBoxCRUD.Controls.Add(this.btnAdd);
            this.groupBoxCRUD.Location = new System.Drawing.Point(380, 350);
            this.groupBoxCRUD.Name = "groupBoxCRUD";
            this.groupBoxCRUD.Size = new System.Drawing.Size(440, 80);
            this.groupBoxCRUD.TabIndex = 2;
            this.groupBoxCRUD.TabStop = false;
            this.groupBoxCRUD.Text = "Операции с БД";
            // 
            // btnDelete
            // 
            this.btnDelete.Location = new System.Drawing.Point(230, 30);
            this.btnDelete.Name = "btnDelete";
            this.btnDelete.Size = new System.Drawing.Size(190, 35);
            this.btnDelete.TabIndex = 1;
            this.btnDelete.Text = "Удалить выбранное";
            this.btnDelete.UseVisualStyleBackColor = true;
            this.btnDelete.Click += new System.EventHandler(this.btnDelete_Click);
            // 
            // btnAdd
            // 
            this.btnAdd.Location = new System.Drawing.Point(20, 30);
            this.btnAdd.Name = "btnAdd";
            this.btnAdd.Size = new System.Drawing.Size(190, 35);
            this.btnAdd.TabIndex = 0;
            this.btnAdd.Text = "Добавить в БД";
            this.btnAdd.UseVisualStyleBackColor = true;
            this.btnAdd.Click += new System.EventHandler(this.btnAdd_Click);
            // 
            // groupBoxMethods
            // 
            this.groupBoxMethods.Controls.Add(this.btnTaxes);
            this.groupBoxMethods.Controls.Add(this.btnReport);
            this.groupBoxMethods.Location = new System.Drawing.Point(380, 440);
            this.groupBoxMethods.Name = "groupBoxMethods";
            this.groupBoxMethods.Size = new System.Drawing.Size(440, 80);
            this.groupBoxMethods.TabIndex = 3;
            this.groupBoxMethods.TabStop = false;
            this.groupBoxMethods.Text = "Методы классов";
            // 
            // btnTaxes
            // 
            this.btnTaxes.Location = new System.Drawing.Point(230, 30);
            this.btnTaxes.Name = "btnTaxes";
            this.btnTaxes.Size = new System.Drawing.Size(190, 35);
            this.btnTaxes.TabIndex = 1;
            this.btnTaxes.Text = "Рассчитать налог";
            this.btnTaxes.UseVisualStyleBackColor = true;
            this.btnTaxes.Click += new System.EventHandler(this.btnTaxes_Click);
            // 
            // btnReport
            // 
            this.btnReport.Location = new System.Drawing.Point(20, 30);
            this.btnReport.Name = "btnReport";
            this.btnReport.Size = new System.Drawing.Size(190, 35);
            this.btnReport.TabIndex = 0;
            this.btnReport.Text = "Вывести отчет";
            this.btnReport.UseVisualStyleBackColor = true;
            this.btnReport.Click += new System.EventHandler(this.btnReport_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 20F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(832, 533);
            this.Controls.Add(this.groupBoxMethods);
            this.Controls.Add(this.groupBoxCRUD);
            this.Controls.Add(this.groupBoxData);
            this.Controls.Add(this.listBoxOrgs);
            this.Name = "Form1";
            this.Text = "Организации (CRUD PostgreSQL)";
            this.groupBoxData.ResumeLayout(false);
            this.groupBoxData.PerformLayout();
            this.groupBoxCRUD.ResumeLayout(false);
            this.groupBoxMethods.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.ListBox listBoxOrgs;
        private System.Windows.Forms.GroupBox groupBoxData;
        private System.Windows.Forms.Label labelName;
        private System.Windows.Forms.TextBox txtName;
        private System.Windows.Forms.Label labelEmployees;
        private System.Windows.Forms.TextBox txtEmployees;
        private System.Windows.Forms.Label labelInn;
        private System.Windows.Forms.TextBox txtInn;
        private System.Windows.Forms.RadioButton rbNonComOrg;
        private System.Windows.Forms.RadioButton rbComOrg;
        private System.Windows.Forms.Label labelSource;
        private System.Windows.Forms.TextBox txtSource;
        private System.Windows.Forms.Label labelPurpose;
        private System.Windows.Forms.TextBox txtPurpose;
        private System.Windows.Forms.Label labelBusinessType;
        private System.Windows.Forms.TextBox txtBusinessType;
        private System.Windows.Forms.Label labelProfit;
        private System.Windows.Forms.TextBox txtProfit;
        private System.Windows.Forms.GroupBox groupBoxCRUD;
        private System.Windows.Forms.Button btnDelete;
        private System.Windows.Forms.Button btnAdd;
        private System.Windows.Forms.GroupBox groupBoxMethods;
        private System.Windows.Forms.Button btnTaxes;
        private System.Windows.Forms.Button btnReport;
    }
}