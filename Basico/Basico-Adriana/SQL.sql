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

SELECT AddressLine1,AddressLine2
FROM Person.Address
WHERE AddressLine2 IS NOT NULL;

SELECT MIN (PostalCode) 
FROM Person.Address;
--FUNCIONES DE AGREGACION
SELECT COUNT (NationalIDNumber) --Cuenta valores distintos al nulo
FROM HumanResources.Employee

SELECT SUM (TaxRate)
FROM Sales.SalesTaxRate;

SELECT AVG (TaxRate)
FROM Sales.SalesTaxRate;

SELECT CardType 
FROM Sales.CreditCard
WHERE ExpMonth IN ('11')

SELECT COUNT(Name)
FROM HumanResources.Department

SELECT SUM(StandardCost)
FROM Production.ProductCostHistory
WHERE ProductID IN ('718')

SELECT AVG(StandardCost) AS "Promedio"
FROM Production.ProductCostHistory
WHERE ProductID BETWEEN 716 AND 720

SELECT CONCAT ("FirstName",' ' , "LastName") AS "Nombre Completo"
FROM Person.Person
WHERE PersonType LIKE ('VC')

--GroupBy a que nivel lo agrego y a que lo agrego
SELECT ProductID, AVG(StandardCost) AS "Standard Cost Max"
FROM Production.ProductCostHistory
GROUP BY ProductID
--A que lo agrego y que agrego
SELECT ProductID, MIN(StandardCost) AS "Standard Cost Min"
FROM Production.ProductCostHistory
GROUP BY ProductID
-- It tells the database to group the rows by the values in the CountryRegionCode column. 
--For each unique country/region code, the query will then calculate the COUNT(Name) for that group.
SELECT CountryRegionCode, COUNT(Name) AS "CountProvince"
FROM Person.StateProvince
GROUP BY CountryRegionCode

SELECT BusinessEntityID, AVG(Rate) AS "AVG-Rate"
FROM HumanResources.EmployeePayHistory
GROUP BY BusinessEntityID;

WITH Temporal1 AS (
	SELECT BusinessEntityID, AVG(Rate) AS AVG_Rate
	FROM HumanResources.EmployeePayHistory	
	GROUP BY BusinessEntityID)

SELECT *
FROM Temporal1
WHERE AVG_Rate > 43
ORDER BY AVG_Rate DESC

--HAVING SIRVE PARA LAS AGREGACIONES EN VEZ DE USAR EL WHERE Y HACER TEMPORALES

SELECT BusinessEntityID, AVG(Rate) AS AVG_Rate
FROM HumanResources.EmployeePayHistory	
GROUP BY BusinessEntityID
HAVING AVG(Rate) > 43 
ORDER BY AVG_Rate ASC

SELECT PostalCode,
CASE 
	WHEN PostalCode = '98055'
	THEN AddressLine1
	ELSE NULL END as Address
FROM Person.Address 

 --CASO REALISTA DE CASE
--SELECT
--	  C.T_CONTACT_ID,
--      C.CONTACT_NUMBER,
--      C.FIRSTNAME, 
--      C.LASTNAME,
--      C.ID_NUMBER,
--      C.BIRTHDATE AS FECHA_DE_NACIMIENTO,
--      -- OBTIENE LA EDAD EN AÑOS BASADA EN LA DIFERENCIA ENTRE LA FECHA ACTUAL Y LA FECHA DE NACIMIENTO
--      CASE 
--            WHEN C.BIRTHDATE IS NULL THEN NULL
--            ELSE FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12)
--        END AS EDAD,
--        CASE 
--            WHEN FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12) IS NULL THEN 'SIN DATO'
--            WHEN FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12) < 18 THEN 'MENOR DE 18'
--            WHEN FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12) <= 24 THEN '18 A 24'
--            WHEN FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12) <= 34 THEN '25 A 34'
--            WHEN FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12) <= 44 THEN '35 A 44'
--            WHEN FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12) <= 54 THEN '45 A 54'
--            WHEN FLOOR(DATEDIFF(MONTH, C.BIRTHDATE, GETDATE()) / 12) <= 64 THEN '55 A 64'
--            ELSE 'MAYOR A 64'
--        END AS RANGO_DE_EDAD

SELECT AddressLine2,
ISNULL(AddressLine2,'N/A')
FROM Person.Address

--INNER JOIN--
SELECT *
FROM HumanResources.Employee
INNER JOIN HumanResources.EmployeeDepartmentHistory
ON HumanResources.EmployeeDepartmentHistory.BusinessEntityID = HumanResources.Employee.BusinessEntityID 

--Obtén una lista de todos los productos junto con el nombre de su subcategoría
SELECT p.Name AS NombreProducto, ps.Name AS Subcategory --Selecciono los nombres de los productos y sibcategorias que deseo
FROM Production.Product p --La tabla de donde deseo sacar la informacion
INNER JOIN Production.ProductSubcategory ps --La tabla con la que la comparo
ON p.ProductSubcategoryID = ps.ProductSubcategoryID --La condicion de comparacion