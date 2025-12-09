from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# Árbol Binario de Búsqueda
class Nodo:
    def __init__(self, producto):
        self.producto = producto
        self.hijo_izquierdo = None
        self.hijo_derecho = None


class ArbolBinario:
    def __init__(self):
        self.raiz = None
    
    def insertar(self, producto):
        if self.raiz is None:
            self.raiz = Nodo(producto)
        else:
            self._insertar_recursivo(self.raiz, producto)
    
    def _insertar_recursivo(self, nodo, producto):
        if int(producto["id"]) < int(nodo.producto["id"]):
            if nodo.hijo_izquierdo is None:
                nodo.hijo_izquierdo = Nodo(producto)
            else:
                self._insertar_recursivo(nodo.hijo_izquierdo, producto)
        else:
            if nodo.hijo_derecho is None:
                nodo.hijo_derecho = Nodo(producto)
            else:
                self._insertar_recursivo(nodo.hijo_derecho, producto)
    
    def buscar(self, id):
        return self._buscar_recursivo(self.raiz, id)
    
    def _buscar_recursivo(self, nodo, id):
        if nodo is None:
            return None
        
        if int(id) == int(nodo.producto["id"]):
            return nodo.producto
        elif int(id) < int(nodo.producto["id"]):
            return self._buscar_recursivo(nodo.hijo_izquierdo, id)
        else:
            return self._buscar_recursivo(nodo.hijo_derecho, id)
    
    def recorrer_inorder(self):
        productos = []
        self._recorrer_inorder_recursivo(self.raiz, productos)
        return productos
    
    def _recorrer_inorder_recursivo(self, nodo, productos):
        if nodo is not None:
            self._recorrer_inorder_recursivo(nodo.hijo_izquierdo, productos)
            productos.append(nodo.producto)
            self._recorrer_inorder_recursivo(nodo.hijo_derecho, productos)


# Lista Enlazada para Pedidos
class NodoPedido:
    def __init__(self, pedido):
        self.pedido = pedido
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
    
    def agregar(self, pedido):
        nuevo_nodo = NodoPedido(pedido)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
    
    def buscar(self, id):
        actual = self.cabeza
        while actual is not None:
            if int(actual.pedido["id"]) == int(id):
                return actual.pedido
            actual = actual.siguiente
        return None
    
    def actualizar(self, id, productos):
        actual = self.cabeza
        while actual is not None:
            if int(actual.pedido["id"]) == int(id):
                actual.pedido["productos"] = productos
                return actual.pedido
            actual = actual.siguiente
        return None
    
    def eliminar(self, id):
        if self.cabeza is None:
            return False
        
        if int(self.cabeza.pedido["id"]) == int(id):
            self.cabeza = self.cabeza.siguiente
            return True
        
        actual = self.cabeza
        while actual.siguiente is not None:
            if int(actual.siguiente.pedido["id"]) == int(id):
                actual.siguiente = actual.siguiente.siguiente
                return True
            actual = actual.siguiente
        
        return False
    
    def listar(self):
        pedidos = []
        actual = self.cabeza
        while actual is not None:
            pedidos.append(actual.pedido)
            actual = actual.siguiente
        return pedidos


# Instancias globales
arbol_productos = ArbolBinario()
lista_pedidos = ListaEnlazada()
contador_pedidos = 0


app = FastAPI(title="Productos y pedidos API", version="1.0.0")


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post("/productos")
async def crear_producto(request: Request):
    data = await request.json()
    
    if "id" not in data or data["id"] is None:
        return JSONResponse(
            status_code=400,
            content={"error": "El campo 'id' es obligatorio"}
        )
    
    producto_id = data["id"]

    if arbol_productos.buscar(producto_id) is not None:
        return JSONResponse(
            status_code=400,
            content={"error": f"Ya existe un producto con ID {producto_id}"}
        )
    
    producto = {
        "id": producto_id,
        "nombre": data.get("nombre"),
        "valor": data.get("valor"),
        "peso": data.get("peso"),
        "descripcion": data.get("descripcion")
    }
    
    arbol_productos.insertar(producto)
    return JSONResponse(status_code=201, content=producto)


@app.get("/productos")
def listar_productos():
    return arbol_productos.recorrer_inorder()


@app.get("/productos/{id}")
def obtener_producto(id: int):
    producto = arbol_productos.buscar(id)
    if producto is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Producto con ID {id} no encontrado"}
        )
    return producto


# Endpoints de pedidos

@app.post("/pedidos")
async def crear_pedido(request: Request):
    global contador_pedidos
    data = await request.json()
    
    if "productos" not in data or data["productos"] is None:
        return JSONResponse(
            status_code=400,
            content={"error": "El campo 'productos' es obligatorio"}
        )
    
    productos_ids = data["productos"]
    
    if not isinstance(productos_ids, list):
        return JSONResponse(
            status_code=400,
            content={"error": "El campo 'productos' debe ser una lista"}
        )
    
    for producto_id in productos_ids:
        if arbol_productos.buscar(producto_id) is None:
            return JSONResponse(
                status_code=400,
                content={"error": f"El producto con ID {producto_id} no existe"}
            )
    
    contador_pedidos += 1
    pedido = {
        "id": contador_pedidos,
        "productos": productos_ids
    }
    
    lista_pedidos.agregar(pedido)
    return JSONResponse(status_code=201, content=pedido)


@app.get("/pedidos")
def listar_pedidos():
    return lista_pedidos.listar()


@app.get("/pedidos/{id}")
def obtener_pedido(id: int):
    pedido = lista_pedidos.buscar(id)
    if pedido is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Pedido con ID {id} no encontrado"}
        )
    return pedido


@app.put("/pedidos/{id}")
async def actualizar_pedido(id: int, request: Request):
    data = await request.json()
    
    if "productos" not in data or data["productos"] is None:
        return JSONResponse(
            status_code=400,
            content={"error": "El campo 'productos' es obligatorio"}
        )
    
    productos_ids = data["productos"]
    
    if not isinstance(productos_ids, list):
        return JSONResponse(
            status_code=400,
            content={"error": "El campo 'productos' debe ser una lista"}
        )
    
    for producto_id in productos_ids:
        if arbol_productos.buscar(producto_id) is None:
            return JSONResponse(
                status_code=400,
                content={"error": f"El producto con ID {producto_id} no existe"}
            )

    pedido_actualizado = lista_pedidos.actualizar(id, productos_ids)
    if pedido_actualizado is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Pedido con ID {id} no encontrado"}
        )
    
    return pedido_actualizado


@app.delete("/pedidos/{id}")
def eliminar_pedido(id: int):
    eliminado = lista_pedidos.eliminar(id)
    if not eliminado:
        return JSONResponse(
            status_code=404,
            content={"error": f"Pedido con ID {id} no encontrado"}
        )
    
    return {"mensaje": f"Pedido {id} eliminado correctamente"}

