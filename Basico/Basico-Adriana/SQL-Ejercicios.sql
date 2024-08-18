--SQL NIVEL BASICO CONSULTAS--
--Selecciona todas las columnas de la tabla Person.Person.
use AdventureWorks2022

SELECT * 
FROM Person.Person

--Selecciona los productos de la tabla Production.Product cuyo precio de lista (ListPrice) sea mayor a $500.
SELECT Name, ListPrice
FROM Production.Product
WHERE ListPrice > 500
ORDER BY ListPrice ASC

--Ordena los clientes (Sales.Customer) por apellido (LastName) en orden descendente.
SELECT sc.CustomerID AS ClienteID,
p.FirstName AS Nombre,
p.LastName AS Apellido
FROM Sales.Customer sc
JOIN Person.Person p ON sc.PersonID = p.BusinessEntityID
ORDER BY p.LastName DESC

--Cuenta cuántos productos hay en cada subcategoría (Production.ProductSubcategory).

SELECT 
ps.name AS NameSubCategory,
COUNT(p.ProductID) AS Cantidad
FROM Production.ProductSubcategory ps
LEFT JOIN Production.Product p
ON ps.ProductSubcategoryID = p.ProductSubcategoryID
GROUP BY ps.Name

--Muestra el nombre del cliente, el nombre del producto y la fecha del pedido para todos los pedidos realizados.
SELECT sc.CustomerID AS ClienteID,
p.FirstName AS Nombre,
p.LastName AS Apellido,
pr.Name AS NombreProducto,
soh.ShipDate AS FechasPedido
FROM Sales.Customer sc
LEFT JOIN Sales.SalesOrderHeader soh ON sc.CustomerID=soh.CustomerID
LEFT JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID=sod.SalesOrderID
LEFT JOIN Production.Product pr ON sod.ProductID = pr.ProductID
JOIN Person.person p ON sc.PersonID = p.BusinessEntityID

--Calcula el precio promedio de los productos en cada subcategoría.
SELECT ProductSubcategoryID, AVG(StandardCost) AS PrecioPromedio
FROM Production.Product 
GROUP BY ProductSubcategoryID

--Muestra los productos que tienen un precio de lista superior al precio promedio de todos los productos.
SELECT Name AS NombreProducto, ListPrice
FROM Production.Product
WHERE ListPrice > (SELECT AVG(ListPrice) FROM Production.Product); --subconsulta dentro de la consulta principal

--Crea una vista que muestre el nombre del cliente, el número total de pedidos y el gasto total.
CREATE VIEW vw_clientegasto AS
SELECT sc.CustomerID AS ClienteID,
p.FirstName AS Nombre,
p.LastName AS Apellido,
OrderQty AS Cantidad, 
UnitPrice*OrderQty As Precio
FROM Sales.Customer sc 
LEFT JOIN Sales.SalesOrderHeader soh ON sc.CustomerID=soh.CustomerID
LEFT JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID=sod.SalesOrderID
JOIN Person.Person p ON sc.PersonID = p.BusinessEntityID

SELECT * FROM vw_clientegasto

--Calcular el porcentaje de ventas de cada producto respecto al total de ventas de su categoría.

WITH PorcentajeVentas AS(
    SELECT pc.ProductCategoryID AS CategoriaID,
	pc.Name AS NombreProducto,
	SUM(pos.UnitPrice*pos.OrderQty) AS Porcentaje
	FROM Production.ProductCategory pc
	LEFT JOIN Production.ProductSubcategory ps ON pc.ProductCategoryID = ps.ProductCategoryID
	LEFT JOIN Production.Product p ON p.ProductSubcategoryID= ps.ProductSubcategoryID
	LEFT JOIN Sales.SalesOrderDetail pos ON pos.ProductID = p.ProductID
	GROUP BY pc.ProductCategoryID, pc.Name, p.Name, p.ProductID
	),

	PorcentajeCategoria AS (
	SELECT CategoriaID AS Categoria,
	SUM (Porcentaje) AS VentasCategoria
	FROM PorcentajeVentas
	GROUP BY CategoriaID
	)

SELECT
  pv.CategoriaID,
  pv.NombreProducto,
  pv.Porcentaje,
  pc.VentasCategoria,
  (pv.Porcentaje / pc.VentasCategoria) * 100 AS PorcentajeTotal
FROM PorcentajeVentas pv
JOIN PorcentajeCategoria pc ON pv.CategoriaID = pc.Categoria
ORDER BY pv.CategoriaID, pv.Porcentaje DESC;

--Analiza el rendimiento de consultas complejas e identifica oportunidades para mejorar el rendimiento utilizando índices.
CREATE NONCLUSTERED INDEX IX_Person_LastName_IncluyeNombres
ON Person.Person (LastName)
INCLUDE (FirstName, MiddleName);
--Asi se utilizaria el indice, poniendo los campos que estan en el indice apra mejorar el rendimiento.
SELECT FirstName, MiddleName, LastName
FROM Person.Person
WHERE LastName = 'Smith';

--Crea un procedimiento almacenado que calcule el gasto total de un cliente dado.

CREATE PROCEDURE GastoTotal_cliente
AS
BEGIN
SELECT sc.CustomerID AS ClienteID,
p.FirstName AS Nombre,
p.LastName AS Apellido,
SUM(sod.UnitPrice*sod.OrderQty) AS TotalVentas
FROM Sales.Customer sc 
LEFT JOIN Sales.SalesOrderHeader soh ON sc.CustomerID = soh.CustomerID
LEFT JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
JOIN Person.Person p ON sc.PersonID = p.BusinessEntityID
GROUP BY sc.CustomerID, p.FirstName, p.LastName
END

EXEC GastoTotal_cliente

