using System;
using System.Collections.Generic;
using Npgsql; // Используем драйвер PostgreSQL

namespace Lab2
{
    public class DatabaseHelper
    {
        // ВНИМАНИЕ: укажите ваш пароль, порт (обычно 5432) и имя созданной БД
        private string connectionString = "Host=localhost;Port=5432;Database=lab2_db;Username=postgres;Password=aklsdfjuqh3t92h3gu32h4go8h235giu23hr8g23n08ufg2h394g;";

        public void InitializeDatabase()
        {
            using (var connection = new NpgsqlConnection(connectionString))
            {
                connection.Open();
                using (var command = connection.CreateCommand())
                {
                    // В PostgreSQL для автоинкремента используется тип SERIAL
                    // ON DELETE CASCADE позволяет удалять дочерние записи при удалении родительской
                    command.CommandText = @"
                        CREATE TABLE IF NOT EXISTS Organizations (
                            Id SERIAL PRIMARY KEY,
                            Name VARCHAR(255) NOT NULL,
                            Inn VARCHAR(50) NOT NULL,
                            Employees INTEGER NOT NULL,
                            OrgType VARCHAR(50) NOT NULL
                        );
                        
                        CREATE TABLE IF NOT EXISTS ComOrgs (
                            Id INTEGER PRIMARY KEY REFERENCES Organizations(Id) ON DELETE CASCADE,
                            Profit INTEGER,
                            BusinessType VARCHAR(255)
                        );
                        
                        CREATE TABLE IF NOT EXISTS NonComOrgs (
                            Id INTEGER PRIMARY KEY REFERENCES Organizations(Id) ON DELETE CASCADE,
                            Purpose TEXT,
                            FoundingSource VARCHAR(255)
                        );
                    ";
                    command.ExecuteNonQuery();
                }
            }
        }

        // CREATE
        public void AddOrganization(Organization org)
        {
            using (var connection = new NpgsqlConnection(connectionString))
            {
                connection.Open();
                using (var transaction = connection.BeginTransaction())
                {
                    using (var command = connection.CreateCommand())
                    {
                        // 1. Добавляем в базовую таблицу и получаем сгенерированный ID через RETURNING
                        string orgType = org is ComOrg ? "ComOrg" : "NonComOrg";
                        command.CommandText = @"
                            INSERT INTO Organizations (Name, Inn, Employees, OrgType) 
                            VALUES (@name, @inn, @employees, @type) 
                            RETURNING Id;";

                        command.Parameters.AddWithValue("name", org.Name);
                        command.Parameters.AddWithValue("inn", org.Inn);
                        command.Parameters.AddWithValue("employees", org.Employees);
                        command.Parameters.AddWithValue("type", orgType);

                        // Получаем ID новой записи
                        int insertedId = Convert.ToInt32(command.ExecuteScalar());

                        // 2. Добавляем в таблицу наследника
                        command.CommandText = "";
                        command.Parameters.Clear();

                        if (org is ComOrg comOrg)
                        {
                            command.CommandText = "INSERT INTO ComOrgs (Id, Profit, BusinessType) VALUES (@id, @profit, @busType)";
                            command.Parameters.AddWithValue("id", insertedId);
                            command.Parameters.AddWithValue("profit", comOrg.Profit);
                            command.Parameters.AddWithValue("busType", comOrg.BusinessType);
                        }
                        else if (org is NonComOrg nonComOrg)
                        {
                            command.CommandText = "INSERT INTO NonComOrgs (Id, Purpose, FoundingSource) VALUES (@id, @purpose, @source)";
                            command.Parameters.AddWithValue("id", insertedId);
                            command.Parameters.AddWithValue("purpose", nonComOrg.Purpose);
                            command.Parameters.AddWithValue("source", nonComOrg.FoundingSource);
                        }

                        command.ExecuteNonQuery();
                        transaction.Commit();
                    }
                }
            }
        }

        // READ
        public List<Organization> GetAllOrganizations()
        {
            var list = new List<Organization>();
            using (var connection = new NpgsqlConnection(connectionString))
            {
                connection.Open();
                using (var command = connection.CreateCommand())
                {
                    // Объединяем таблицы через LEFT JOIN
                    command.CommandText = @"
                        SELECT o.Id, o.Name, o.Inn, o.Employees, o.OrgType,
                               c.Profit, c.BusinessType,
                               n.Purpose, n.FoundingSource
                        FROM Organizations o
                        LEFT JOIN ComOrgs c ON o.Id = c.Id
                        LEFT JOIN NonComOrgs n ON o.Id = n.Id
                        ORDER BY o.Id;
                    ";

                    using (var reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            int id = reader.GetInt32(0);
                            string name = reader.GetString(1);
                            string inn = reader.GetString(2);
                            int emp = reader.GetInt32(3);
                            string type = reader.GetString(4);

                            if (type == "ComOrg")
                            {
                                int profit = reader.IsDBNull(5) ? 0 : reader.GetInt32(5);
                                string busType = reader.IsDBNull(6) ? "" : reader.GetString(6);
                                list.Add(new ComOrg(id, name, inn, emp, profit, busType));
                            }
                            else if (type == "NonComOrg")
                            {
                                string purpose = reader.IsDBNull(7) ? "" : reader.GetString(7);
                                string source = reader.IsDBNull(8) ? "" : reader.GetString(8);
                                list.Add(new NonComOrg(id, name, inn, emp, purpose, source));
                            }
                        }
                    }
                }
            }
            return list;
        }

        // DELETE
        public void DeleteOrganization(int id)
        {
            using (var connection = new NpgsqlConnection(connectionString))
            {
                connection.Open();
                using (var command = connection.CreateCommand())
                {
                    // Благодаря ON DELETE CASCADE дочерние записи удалятся автоматически
                    command.CommandText = "DELETE FROM Organizations WHERE Id = @id;";
                    command.Parameters.AddWithValue("id", id);
                    command.ExecuteNonQuery();
                }
            }
        }

        // UPDATE (Пример реализации для полноты CRUD)
        public void UpdateOrganization(Organization org)
        {
            using (var connection = new NpgsqlConnection(connectionString))
            {
                connection.Open();
                using (var transaction = connection.BeginTransaction())
                {
                    using (var command = connection.CreateCommand())
                    {
                        // Обновляем базовую таблицу
                        command.CommandText = "UPDATE Organizations SET Name = @name, Inn = @inn, Employees = @emp WHERE Id = @id";
                        command.Parameters.AddWithValue("id", org.Id);
                        command.Parameters.AddWithValue("name", org.Name);
                        command.Parameters.AddWithValue("inn", org.Inn);
                        command.Parameters.AddWithValue("emp", org.Employees);
                        command.ExecuteNonQuery();

                        command.Parameters.Clear();

                        // Обновляем дочернюю таблицу
                        if (org is ComOrg comOrg)
                        {
                            command.CommandText = "UPDATE ComOrgs SET Profit = @profit, BusinessType = @busType WHERE Id = @id";
                            command.Parameters.AddWithValue("id", org.Id);
                            command.Parameters.AddWithValue("profit", comOrg.Profit);
                            command.Parameters.AddWithValue("busType", comOrg.BusinessType);
                        }
                        else if (org is NonComOrg nonComOrg)
                        {
                            command.CommandText = "UPDATE NonComOrgs SET Purpose = @purpose, FoundingSource = @source WHERE Id = @id";
                            command.Parameters.AddWithValue("id", org.Id);
                            command.Parameters.AddWithValue("purpose", nonComOrg.Purpose);
                            command.Parameters.AddWithValue("source", nonComOrg.FoundingSource);
                        }
                        command.ExecuteNonQuery();

                        transaction.Commit();
                    }
                }
            }
        }
    }
}