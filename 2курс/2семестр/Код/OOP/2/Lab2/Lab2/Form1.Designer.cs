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
            listBoxOrgs = new ListBox();
            groupBoxData = new GroupBox();
            UpdateButton = new Button();
            labelSource = new Label();
            txtSource = new TextBox();
            labelPurpose = new Label();
            txtPurpose = new TextBox();
            labelBusinessType = new Label();
            txtBusinessType = new TextBox();
            labelProfit = new Label();
            txtProfit = new TextBox();
            rbNonComOrg = new RadioButton();
            rbComOrg = new RadioButton();
            labelEmployees = new Label();
            txtEmployees = new TextBox();
            labelInn = new Label();
            txtInn = new TextBox();
            labelName = new Label();
            txtName = new TextBox();
            groupBoxCRUD = new GroupBox();
            btnDelete = new Button();
            btnAdd = new Button();
            groupBoxMethods = new GroupBox();
            button2 = new Button();
            button1 = new Button();
            btnTaxes = new Button();
            btnReport = new Button();
            label1 = new Label();
            info1 = new TextBox();
            label2 = new Label();
            info2 = new TextBox();
            label3 = new Label();
            info3 = new TextBox();
            label4 = new Label();
            info4 = new TextBox();
            button4 = new Button();
            groupBoxData.SuspendLayout();
            groupBoxCRUD.SuspendLayout();
            groupBoxMethods.SuspendLayout();
            SuspendLayout();
            // 
            // listBoxOrgs
            // 
            listBoxOrgs.FormattingEnabled = true;
            listBoxOrgs.Location = new Point(12, 12);
            listBoxOrgs.Name = "listBoxOrgs";
            listBoxOrgs.Size = new Size(350, 504);
            listBoxOrgs.TabIndex = 0;
            listBoxOrgs.SelectedIndexChanged += UpdateListBoxSelection;
            // 
            // groupBoxData
            // 
            groupBoxData.Controls.Add(UpdateButton);
            groupBoxData.Controls.Add(labelSource);
            groupBoxData.Controls.Add(txtSource);
            groupBoxData.Controls.Add(labelPurpose);
            groupBoxData.Controls.Add(txtPurpose);
            groupBoxData.Controls.Add(labelBusinessType);
            groupBoxData.Controls.Add(txtBusinessType);
            groupBoxData.Controls.Add(labelProfit);
            groupBoxData.Controls.Add(txtProfit);
            groupBoxData.Controls.Add(rbNonComOrg);
            groupBoxData.Controls.Add(rbComOrg);
            groupBoxData.Controls.Add(labelEmployees);
            groupBoxData.Controls.Add(txtEmployees);
            groupBoxData.Controls.Add(labelInn);
            groupBoxData.Controls.Add(txtInn);
            groupBoxData.Controls.Add(labelName);
            groupBoxData.Controls.Add(txtName);
            groupBoxData.Location = new Point(380, 12);
            groupBoxData.Name = "groupBoxData";
            groupBoxData.Size = new Size(440, 330);
            groupBoxData.TabIndex = 1;
            groupBoxData.TabStop = false;
            groupBoxData.Text = "Данные организации";
            // 
            // UpdateButton
            // 
            UpdateButton.Location = new Point(340, -1);
            UpdateButton.Name = "UpdateButton";
            UpdateButton.Size = new Size(94, 29);
            UpdateButton.TabIndex = 2;
            UpdateButton.Text = "Обновить";
            UpdateButton.UseVisualStyleBackColor = true;
            UpdateButton.Click += btnUpdate_Click;
            // 
            // labelSource
            // 
            labelSource.AutoSize = true;
            labelSource.Location = new Point(15, 290);
            labelSource.Name = "labelSource";
            labelSource.Size = new Size(78, 20);
            labelSource.TabIndex = 15;
            labelSource.Text = "Источник:";
            // 
            // txtSource
            // 
            txtSource.Location = new Point(130, 287);
            txtSource.Name = "txtSource";
            txtSource.Size = new Size(290, 27);
            txtSource.TabIndex = 14;
            // 
            // labelPurpose
            // 
            labelPurpose.AutoSize = true;
            labelPurpose.Location = new Point(15, 257);
            labelPurpose.Name = "labelPurpose";
            labelPurpose.Size = new Size(47, 20);
            labelPurpose.TabIndex = 13;
            labelPurpose.Text = "Цель:";
            // 
            // txtPurpose
            // 
            txtPurpose.Location = new Point(130, 254);
            txtPurpose.Name = "txtPurpose";
            txtPurpose.Size = new Size(290, 27);
            txtPurpose.TabIndex = 12;
            // 
            // labelBusinessType
            // 
            labelBusinessType.AutoSize = true;
            labelBusinessType.Location = new Point(15, 224);
            labelBusinessType.Name = "labelBusinessType";
            labelBusinessType.Size = new Size(99, 20);
            labelBusinessType.TabIndex = 11;
            labelBusinessType.Text = "Тип бизнеса:";
            // 
            // txtBusinessType
            // 
            txtBusinessType.Location = new Point(130, 221);
            txtBusinessType.Name = "txtBusinessType";
            txtBusinessType.Size = new Size(290, 27);
            txtBusinessType.TabIndex = 10;
            // 
            // labelProfit
            // 
            labelProfit.AutoSize = true;
            labelProfit.Location = new Point(15, 191);
            labelProfit.Name = "labelProfit";
            labelProfit.Size = new Size(77, 20);
            labelProfit.TabIndex = 9;
            labelProfit.Text = "Прибыль:";
            // 
            // txtProfit
            // 
            txtProfit.Location = new Point(130, 188);
            txtProfit.Name = "txtProfit";
            txtProfit.Size = new Size(290, 27);
            txtProfit.TabIndex = 8;
            // 
            // rbNonComOrg
            // 
            rbNonComOrg.AutoSize = true;
            rbNonComOrg.Location = new Point(230, 140);
            rbNonComOrg.Name = "rbNonComOrg";
            rbNonComOrg.Size = new Size(150, 24);
            rbNonComOrg.TabIndex = 7;
            rbNonComOrg.Text = "Некоммерческая";
            rbNonComOrg.UseVisualStyleBackColor = true;
            // 
            // rbComOrg
            // 
            rbComOrg.AutoSize = true;
            rbComOrg.Checked = true;
            rbComOrg.Location = new Point(70, 140);
            rbComOrg.Name = "rbComOrg";
            rbComOrg.Size = new Size(133, 24);
            rbComOrg.TabIndex = 6;
            rbComOrg.TabStop = true;
            rbComOrg.Text = "Коммерческая";
            rbComOrg.UseVisualStyleBackColor = true;
            rbComOrg.CheckedChanged += rbComOrg_CheckedChanged;
            // 
            // labelEmployees
            // 
            labelEmployees.AutoSize = true;
            labelEmployees.Location = new Point(15, 103);
            labelEmployees.Name = "labelEmployees";
            labelEmployees.Size = new Size(94, 20);
            labelEmployees.TabIndex = 5;
            labelEmployees.Text = "Сотрудники:";
            // 
            // txtEmployees
            // 
            txtEmployees.Location = new Point(130, 100);
            txtEmployees.Name = "txtEmployees";
            txtEmployees.Size = new Size(290, 27);
            txtEmployees.TabIndex = 4;
            // 
            // labelInn
            // 
            labelInn.AutoSize = true;
            labelInn.Location = new Point(15, 70);
            labelInn.Name = "labelInn";
            labelInn.Size = new Size(45, 20);
            labelInn.TabIndex = 3;
            labelInn.Text = "ИНН:";
            // 
            // txtInn
            // 
            txtInn.Location = new Point(130, 67);
            txtInn.Name = "txtInn";
            txtInn.Size = new Size(290, 27);
            txtInn.TabIndex = 2;
            // 
            // labelName
            // 
            labelName.AutoSize = true;
            labelName.Location = new Point(15, 37);
            labelName.Name = "labelName";
            labelName.Size = new Size(80, 20);
            labelName.TabIndex = 1;
            labelName.Text = "Название:";
            // 
            // txtName
            // 
            txtName.Location = new Point(130, 34);
            txtName.Name = "txtName";
            txtName.Size = new Size(290, 27);
            txtName.TabIndex = 0;
            // 
            // groupBoxCRUD
            // 
            groupBoxCRUD.Controls.Add(btnDelete);
            groupBoxCRUD.Controls.Add(btnAdd);
            groupBoxCRUD.Location = new Point(380, 350);
            groupBoxCRUD.Name = "groupBoxCRUD";
            groupBoxCRUD.Size = new Size(440, 80);
            groupBoxCRUD.TabIndex = 2;
            groupBoxCRUD.TabStop = false;
            groupBoxCRUD.Text = "Операции с БД";
            // 
            // btnDelete
            // 
            btnDelete.Location = new Point(230, 30);
            btnDelete.Name = "btnDelete";
            btnDelete.Size = new Size(190, 35);
            btnDelete.TabIndex = 1;
            btnDelete.Text = "Удалить выбранное";
            btnDelete.UseVisualStyleBackColor = true;
            btnDelete.Click += btnDelete_Click;
            // 
            // btnAdd
            // 
            btnAdd.Location = new Point(20, 30);
            btnAdd.Name = "btnAdd";
            btnAdd.Size = new Size(190, 35);
            btnAdd.TabIndex = 0;
            btnAdd.Text = "Добавить в БД";
            btnAdd.UseVisualStyleBackColor = true;
            btnAdd.Click += btnAdd_Click;
            // 
            // groupBoxMethods
            // 
            groupBoxMethods.Controls.Add(button2);
            groupBoxMethods.Controls.Add(button1);
            groupBoxMethods.Controls.Add(btnTaxes);
            groupBoxMethods.Controls.Add(btnReport);
            groupBoxMethods.Location = new Point(380, 440);
            groupBoxMethods.Name = "groupBoxMethods";
            groupBoxMethods.Size = new Size(440, 127);
            groupBoxMethods.TabIndex = 3;
            groupBoxMethods.TabStop = false;
            groupBoxMethods.Text = "Методы классов";
            // 
            // button2
            // 
            button2.Location = new Point(230, 86);
            button2.Name = "button2";
            button2.Size = new Size(190, 35);
            button2.TabIndex = 3;
            button2.Text = "Уникальная функция 2";
            button2.UseVisualStyleBackColor = true;
            button2.Click += btnUnique2;
            // 
            // button1
            // 
            button1.Location = new Point(20, 86);
            button1.Name = "button1";
            button1.Size = new Size(190, 35);
            button1.TabIndex = 2;
            button1.Text = "Уникальная функция 1";
            button1.UseVisualStyleBackColor = true;
            button1.Click += btnUnique1;
            // 
            // btnTaxes
            // 
            btnTaxes.Location = new Point(230, 30);
            btnTaxes.Name = "btnTaxes";
            btnTaxes.Size = new Size(190, 35);
            btnTaxes.TabIndex = 1;
            btnTaxes.Text = "Рассчитать налог";
            btnTaxes.UseVisualStyleBackColor = true;
            btnTaxes.Click += btnTaxes_Click;
            // 
            // btnReport
            // 
            btnReport.Location = new Point(20, 30);
            btnReport.Name = "btnReport";
            btnReport.Size = new Size(190, 35);
            btnReport.TabIndex = 0;
            btnReport.Text = "Вывести отчет";
            btnReport.UseVisualStyleBackColor = true;
            btnReport.Click += btnReport_Click;
            // 
            // label1
            // 
            label1.AutoSize = true;
            label1.Location = new Point(9, 576);
            label1.Name = "label1";
            label1.Size = new Size(77, 20);
            label1.TabIndex = 11;
            label1.Text = "Прибыль:";
            label1.Click += UpdateListBoxSelection;
            // 
            // info1
            // 
            info1.Location = new Point(124, 573);
            info1.Name = "info1";
            info1.Size = new Size(290, 27);
            info1.TabIndex = 10;
            // 
            // label2
            // 
            label2.AutoSize = true;
            label2.Location = new Point(9, 609);
            label2.Name = "label2";
            label2.Size = new Size(99, 20);
            label2.TabIndex = 13;
            label2.Text = "Тип бизнеса:";
            // 
            // info2
            // 
            info2.Location = new Point(124, 606);
            info2.Name = "info2";
            info2.Size = new Size(290, 27);
            info2.TabIndex = 12;
            // 
            // label3
            // 
            label3.AutoSize = true;
            label3.Location = new Point(9, 642);
            label3.Name = "label3";
            label3.Size = new Size(78, 20);
            label3.TabIndex = 15;
            label3.Text = "Источник:";
            // 
            // info3
            // 
            info3.Location = new Point(124, 639);
            info3.Name = "info3";
            info3.Size = new Size(290, 27);
            info3.TabIndex = 14;
            // 
            // label4
            // 
            label4.AutoSize = true;
            label4.Location = new Point(9, 672);
            label4.Name = "label4";
            label4.Size = new Size(47, 20);
            label4.TabIndex = 17;
            label4.Text = "Цель:";
            // 
            // info4
            // 
            info4.Location = new Point(124, 669);
            info4.Name = "info4";
            info4.Size = new Size(290, 27);
            info4.TabIndex = 16;
            // 
            // button4
            // 
            button4.Location = new Point(179, 526);
            button4.Name = "button4";
            button4.Size = new Size(94, 29);
            button4.TabIndex = 18;
            button4.Text = "Изменить";
            button4.UseVisualStyleBackColor = true;
            button4.Click += button4_Click;
            // 
            // Form1
            // 
            AutoScaleDimensions = new SizeF(8F, 20F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(832, 708);
            Controls.Add(button4);
            Controls.Add(label4);
            Controls.Add(info4);
            Controls.Add(label3);
            Controls.Add(info3);
            Controls.Add(label2);
            Controls.Add(info2);
            Controls.Add(label1);
            Controls.Add(info1);
            Controls.Add(groupBoxMethods);
            Controls.Add(groupBoxCRUD);
            Controls.Add(groupBoxData);
            Controls.Add(listBoxOrgs);
            Name = "Form1";
            Text = "Организации (CRUD PostgreSQL)";
            Load += Form1_Load;
            groupBoxData.ResumeLayout(false);
            groupBoxData.PerformLayout();
            groupBoxCRUD.ResumeLayout(false);
            groupBoxMethods.ResumeLayout(false);
            ResumeLayout(false);
            PerformLayout();

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
        private Button UpdateButton;
        private Button button2;
        private Button button1;
        private Label label1;
        private TextBox info1;
        private Label label2;
        private TextBox info2;
        private Label label3;
        private TextBox info3;
        private Label label4;
        private TextBox info4;
        private Button button4;
    }
}