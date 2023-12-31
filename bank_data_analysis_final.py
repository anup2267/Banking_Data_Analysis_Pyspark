# -*- coding: utf-8 -*-
"""Bank_Data_Analysis_Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13cLiQ-ymTrvSPTP4dBc-zUP8FIhQVa7N
"""

#install Apache Spark 3.0.1 with Hadoop 2.7 from here.
!wget https://archive.apache.org/dist/spark/spark-3.0.0/spark-3.0.0-bin-hadoop2.7.tgz

# Now, we just need to unzip that folder.
!tar -xvzf spark-3.0.0-bin-hadoop2.7.tgz
!pip install findspark


import os
os.environ["SPARK_HOME"] = "/content/spark-3.0.0-bin-hadoop2.7"
import findspark
findspark.init()

"""**Customer And Employees Data Load**"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType
from pyspark.sql.functions import col

# Create Spark session
spark = SparkSession.builder \
    .appName("CombinedExample") \
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.17.0") \
    .config('spark.jars','sqlite-jdbc-3.44.1.0.jar') \
    .master("local") \
    .getOrCreate()


# Define database properties and connection URL
db_properties = {"driver": "org.sqlite.JDBC"}
connection_url = "jdbc:sqlite:/content/customers.db"

# Read data from the database with the original schema
customers_df = spark.read.jdbc(connection_url, 'customers', properties=db_properties)

# Define the altered schema
altered_schema = StructType([
    StructField("customer_id", IntegerType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("date_of_birth", DateType(), True)
])

# Apply the altered schema to the DataFrame
customer_df = customers_df \
    .withColumn("date_of_birth", col("date_of_birth").cast("date"))  # Convert StringType to DateType

# Display the DataFrame with the altered schema
customer_df.printSchema()
customer_df.show()


# Define the path to your XML file
xml_file_path = "/content/employees.xml"

# Read XML data using the DataFrame API
employees_df = spark.read.format("xml").option("rowTag", "DATA_RECORD").load(xml_file_path)



# Change schema to integer for branch_id and employee_id columns
employees_df = employees_df.withColumn("branch_id", col("branch_id").cast("integer"))
employees_df = employees_df.withColumn("employee_id", col("employee_id").cast("integer"))

# Print the updated schema
employees_df.printSchema()
employees_df.show()

"""**Tansaction_Data_Load**"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType

# Create a SparkSession
#spark = SparkSession.builder.appName("Transaction_Data_Load").getOrCreate()

# Define the new schema for transactions
transactions_schema = StructType([
    StructField("transaction_id", IntegerType(), True),
    StructField("account_id", IntegerType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("transaction_date", TimestampType(), True)
])

# Read the CSV file with the specified schema
transactions_df = spark.read.csv("/content/transactions.csv", header=True, schema=transactions_schema)

# Show the DataFrame
transactions_df.show()

# Print the schema
transactions_df.printSchema()

"""**Loan Data Load**"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, DateType, StringType

# Create a SparkSession
#spark = SparkSession.builder.appName("Loan_Data_Load").getOrCreate()

# Define the schema
schema = StructType([
    StructField("loan_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("loan_amount", IntegerType(), True),
    StructField("interest_rate", DoubleType(), True),
    StructField("start_date", DateType(), True),
    StructField("end_date", DateType(), True),
    StructField("status", StringType(), True)
])

# Path to your CSV file
csv_file_path = "/content/loans.csv"

# Create a DataFrame by reading from the CSV file with the specified schema
loans_df = spark.read.csv(csv_file_path, header=True, schema=schema)

# Show the DataFrame
loans_df.show()

# Print the schema
loans_df.printSchema()

"""**Account Data Load**"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Create a Spark session
#spark = SparkSession.builder.appName("AccountAnalysis").getOrCreate()

# Read the JSON file with the nested structure
accounts_df = spark.read.option("multiLine", True).json("/content/accounts.json")

# Explode the nested array of accounts
exploded_accounts_df = accounts_df.select(explode("accounts").alias("account"))

# Flatten the exploded structure and split the arrays into separate columns
flattened_accounts_df = exploded_accounts_df.select(
    col("account.account_id").alias("account_id"),
    col("account.customer_id").alias("customer_id"),
    col("account.employee_id").alias("employee_id"),
    col("account.account_type").alias("account_type"),
    col("account.balance").alias("balance")
)

# Change the data type of the balance column to double
flattened_accounts_df = flattened_accounts_df.withColumn("balance", col("balance").cast("double"))

# Change the data type of account_id, customer_id, and employee_id columns to integer
flattened_accounts_df = flattened_accounts_df.withColumn("account_id", col("account_id").cast("integer"))
flattened_accounts_df = flattened_accounts_df.withColumn("customer_id", col("customer_id").cast("integer"))
flattened_accounts_df = flattened_accounts_df.withColumn("employee_id", col("employee_id").cast("integer"))

# Show the flattened DataFrame
flattened_accounts_df.show()

# Assign the flattened DataFrame back to the original variable
accounts_df = flattened_accounts_df
accounts_df.printSchema()

"""**Payment_History Data Load**"""

from pyspark.sql.functions import monotonically_increasing_id

# Read the Parquet file
payment_history_df = spark.read.parquet("/content/payment_history.parquet")

# Add an auto-incrementing column payment_id
payment_history_df = payment_history_df.withColumn("payment_id", monotonically_increasing_id())

# Show the DataFrame with the added payment_id column
payment_history_df.show()
payment_history_df.printSchema()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Create a Spark session
#spark = SparkSession.builder.appName("BranchAnalysis").getOrCreate()

# Read the JSON file with the nested structure
branches_df = spark.read.option("multiLine", True).json("/content/branches.json")

# Explode the nested array of branches
exploded_branches_df = branches_df.select(explode("branches").alias("branch"))

# Flatten the exploded structure and split the arrays into separate columns
flattened_branches_df = exploded_branches_df.select(
    col("branch.branch_id").alias("branch_id"),
    col("branch.branch_name").alias("branch_name"),
    col("branch.location").alias("location")
)

# Change the data type of the branch_id column to integer
flattened_branches_df = flattened_branches_df.withColumn("branch_id", col("branch_id").cast("integer"))

# Show the flattened DataFrame
flattened_branches_df.show()

# Assign the flattened DataFrame back to the original variable
branches_df = flattened_branches_df
branches_df.printSchema()

"""**Basic Reports**"""

import pyspark.sql.functions as F
# Basic Reports
# 1. Show the balance amount for an account_id = 1:
account_balance_df = accounts_df.filter(accounts_df["account_id"] == 1).groupBy("account_id").agg({"balance": "sum"})
print("Show the balance amount for an account_id = 1:")
account_balance_df.show()

# 2. List Transactions for an account_id = 1:
print("List Transactions for an account_id = 1:")
transactions_df.filter(transactions_df["account_id"] == 1).show()

# 3. List Accounts with a zero balance:
zero_balance_accounts_df = accounts_df.filter(accounts_df["balance"] == 0)
print("List Accounts with a zero balance:")
zero_balance_accounts_df.show()

# 4. Find the Oldest Customer:
oldest_customer_df = customers_df.orderBy("date_of_birth").limit(1)
print("Find the Oldest Customer:")
oldest_customer_df.show()

# 5. Calculate the Total Interest Earned Across All Accounts:
total_interest_df = loans_df.groupBy().agg(F.sum("interest_rate"))
print("Calculate the Total Interest Earned Across All Accounts:")
total_interest_df.show()

"""**Accounts Reports**"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as spark_sum

# Create a Spark session
#spark = SparkSession.builder.appName("AccountReports").getOrCreate()


# 1. List All Accounts with Customer Information:
all_accounts_info_df = accounts_df.join(customers_df.withColumnRenamed("id", "customer_id"), "customer_id")
print("List All Accounts with Customer Information:")
all_accounts_info_df.show()

# 2. Calculate Total Balance for Each Customer:
total_balance_per_customer_df = accounts_df.groupBy("customer_id").agg(spark_sum("balance").alias("total_balance"))
print("Calculate Total Balance for Each Customer:")
total_balance_per_customer_df.show()

# 3. Find Customers with Multiple Accounts:
customers_multiple_accounts_df = accounts_df.groupBy("customer_id").count().filter("count > 1")
print("Find Customers with Multiple Accounts:")
customers_multiple_accounts_df.show()

"""**Customer Transactions Reports**"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum as spark_sum

# Create a Spark session
#spark = SparkSession.builder.appName("TransactionReports").getOrCreate()



# 1. List Transactions with Account and Customer Information:
transactions_customer_info_df = (
    transactions_df
    .join(accounts_df, transactions_df["account_id"] == accounts_df["account_id"])
    .join(customers_df, accounts_df["customer_id"] == customers_df["id"])
)
print("List Transactions with Account and Customer Information:")
transactions_customer_info_df.show()

# 2. Calculate Average Transaction Amount:
avg_transaction_amount_df = transactions_df.groupBy().agg(avg("amount").alias("average_transaction_amount"))
print("Calculate Average Transaction Amount:")
avg_transaction_amount_df.show()

# 3. Identify High-Value Customers with Total Balance:
threshold_value = 10000
high_value_customers_df = (
    transactions_df
    .join(accounts_df, transactions_df["account_id"] == accounts_df["account_id"])
    .groupBy("customer_id")
    .agg(spark_sum("balance").alias("total_balance"))
    .filter(col("total_balance") > threshold_value)
)
print("Identify High-Value Customers with Total Balance:")
high_value_customers_df.show()

"""**Additional Reports**"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max as spark_max, count, sum as spark_sum, avg

# Create a Spark session
#spark = SparkSession.builder.appName("AdditionalReports").getOrCreate()



# 1. List Employees and Their Assigned Customers:
employees_customers_df = employees_df.join(customers_df, employees_df["employee_id"] == customers_df["id"])
print("List Employees and Their Assigned Customers:")
employees_customers_df.show()

# 2. Calculate the Total Number of Transactions for Each Account Type:
transactions_account_type_df = transactions_df.join(accounts_df, "account_id")
total_transactions_account_type_df = transactions_account_type_df.groupBy("account_type").agg(count("*").alias("total_transactions"))
print("Calculate the Total Number of Transactions for Each Account Type:")
total_transactions_account_type_df.show()

# 3. Find Customers with No Accounts:
customers_no_accounts_df = customers_df.join(accounts_df, customers_df["id"] == accounts_df["customer_id"], "left_outer").filter(accounts_df["customer_id"].isNull())
print("Find Customers with No Accounts:")
customers_no_accounts_df.show()

# 4. List the Latest Transaction for Each Account:
latest_transaction_df = (
    transactions_df
    .groupBy("account_id")
    .agg(spark_max("transaction_date").alias("latest_transaction_date"))
)
print("List the Latest Transaction for Each Account:")
latest_transaction_df.show()

joined_df = transactions_df.join(accounts_df, "account_id")

# 5. Calculate the Total Withdrawals for Each Customer:
withdrawals_per_customer_df = (
    joined_df
    .filter(joined_df["transaction_type"] == "Withdrawal")
    .groupBy("customer_id")
    .agg(spark_sum("amount").alias("total_withdrawals"))
)
print("Calculate the Total Withdrawals for Each Customer:")
withdrawals_per_customer_df.show()

# 6. Find Duplicate Transactions:
duplicate_transactions_df = transactions_df.groupBy("transaction_id").agg(count("*").alias("count")).filter("count > 1")
print("Find Duplicate Transactions:")
duplicate_transactions_df.show()

# Install necessary packages
!pip install pyspark matplotlib

# Import required libraries
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt

# Create a Spark session
spark = SparkSession.builder.appName("BankDataAnalysis").getOrCreate()

# Load your data (assuming you've loaded the necessary DataFrames)

# Example: Visualize Total Balance Per Customer

# Calculate Total Balance for Each Customer
total_balance_per_customer_df = accounts_df.groupBy("customer_id").agg({"balance": "sum"})

# Convert Spark DataFrame to Pandas DataFrame for plotting
total_balance_pandas_df = total_balance_per_customer_df.toPandas()

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(total_balance_pandas_df["customer_id"], total_balance_pandas_df["sum(balance)"])
plt.title("Total Balance Per Customer")
plt.xlabel("Customer ID")
plt.ylabel("Total Balance")
plt.show()

# Stop the Spark session when done
#spark.stop()