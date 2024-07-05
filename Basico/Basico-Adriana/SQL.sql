--SELECCIONAR TODAS LAS COLUMNAS DE UNA TABLA--

SELECT * FROM Person.Person;

--SELECCIONAR COLUMNAS ESPECIFICAS DE UNA TABLA--

SELECT FirstName, LastName FROM Person.Person;

--FILTROS CON WHERE--

SELECT *
FROM Sales.CreditCard
WHERE ExpYear>2006;

SELECT *
FROM Sales.CreditCard
WHERE ExpYear BETWEEN 2005 AND 2018;

SELECT *
FROM Sales.CreditCard
WHERE CardType = 'SuperiorCard';

SELECT *
FROM Sales.CreditCard
WHERE CardNumber LIKE '11111%';

SELECT *
FROM Sales.CreditCard
WHERE CardNumber LIKE '11111%' AND ExpMonth < 5;

SELECT Name, ProductNumber
FROM Production.Product
WHERE SafetyStockLevel = 500;

SELECT Quantity, TransactionType, (Quantity * ActualCost) AS Total
FROM Production.TransactionHistory
WHERE Quantity >= 15;

SELECT COUNT(*) AS NumEmpleados, MAX(Gender) AS Nacimiento
FROM HumanResources.Employee;

--ORDER BY POR COLUMNA

SELECT NationalIDNumber
FROM HumanResources.Employee
ORDER BY JobTitle ASC;  -- Ordenar por apellido de A a Z

SELECT Name, StandardCost, ProductID
FROM Production.Product
ORDER BY StandardCost DESC, ProductID ASC;  -- Ordenar por precio (mayor a menor) y luego por cantidad (menor a mayor)

SELECT DISTINCT ProductModelID
FROM Production.Product;

use AdventureWorks2022

SELECT DISTINCT JobTitle
FROM HumanResources.Employee;

SELECT DISTINCT AddressLine1 
FROM Person.Address
WHERE PostalCode LIKE '98%';

SELECT DISTINCT LoginID,BusinessEntityID
FROM HumanResources.Employee
WHERE JobTitle LIKE 'PRODUCTION%' 
ORDER BY BusinessEntityID DESC;

SELECT NationalIDNumber, JobTitle
FROM HumanResources.Employee
WHERE JobTitle NOT LIKE 'Research%';