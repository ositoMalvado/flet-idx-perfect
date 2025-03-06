import asyncio
import aiohttp
from typing import Dict, Any, List
import math

GLOBAL_DEBUG = False


class RusSession:
    def __init__(self, usuario: str, password: str, codigos: List[str]):
        self.usuario = usuario
        self.password = password
        self.codigos = codigos
        self._cliente = None
        self._event_loop = None

    def start(self):
        """Inicia la sesión y autentica"""
        if not self._event_loop or self._event_loop.is_closed():
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)

        self._cliente = self._event_loop.run_until_complete(
            APIClientRUS.create(self.usuario, self.password, self.codigos)
        )

    def refacturar_propuestas(
        self,
        propuestas: List[Dict[str, Any]],
        datos_refactura: Dict[str, Any] = None,
        callback_refactura=None,
        callback_success=None,
    ):
        """
        Refactura una lista de propuestas, usando un cliente asincrónico.

        Args:
            propuestas (List[Dict[str, Any]]): Lista de propuestas a refacturar.
            datos_refactura (Dict[str, Any], optional): Datos de refactura base. Defaults to None.
            callback_refactura (callable, optional): Función callback para datos de refactura dinámicos. Defaults to None.

        Returns:
            Any: Resultado de la refacturación (depende de la función asincrónica subyacente).
        Raises:
            Exception: Si la sesión no ha sido iniciada.
        """
        if not self._cliente:
            raise Exception("Sesión no iniciada. Ejecuta start() primero")
        return self._event_loop.run_until_complete(
            self._cliente.refacturar_propuestas(
                propuestas,
                datos_refactura,
                callback_refactura=callback_refactura,
                callback_success=callback_success,
            )
        )

    def refacturar_propuesta(
        self,
        propuesta: List[Dict[str, Any]],
        datos_refactura: Dict[str, Any] = None,
        callback_refactura=None,
    ):
        """
        Refactura una propuesta individual, usando un cliente asincrónico.

        Args:
            propuesta (List[Dict[str, Any]]): Lista conteniendo la propuesta a refacturar.
            datos_refactura (Dict[str, Any], optional): Datos de refactura base. Defaults to None.
            callback_refactura (callable, optional): Función callback para datos de refactura dinámicos. Defaults to None.

        Returns:
            Any: Resultado de la refacturación (depende de la función asincrónica subyacente).
        Raises:
            Exception: Si la sesión no ha sido iniciada.
        """
        if not self._cliente:
            raise Exception("Sesión no iniciada. Ejecuta start() primero")
        return self._event_loop.run_until_complete(
            self._cliente.refacturar_propuesta(
                propuesta, datos_refactura, callback_refactura=callback_refactura
            )
        )

    def buscar_propuestas(self) -> List[Dict[str, Any]]:
        """Obtiene todas las propuestas (bloqueante)"""
        if not self._cliente:
            raise Exception("Sesión no iniciada. Ejecuta start() primero")

        return self._event_loop.run_until_complete(self._cliente.obtener_propuestas())

    def stop(self):
        """Cierra la sesión y libera recursos"""
        if self._cliente:
            self._event_loop.run_until_complete(self._cliente.cerrar_sesion())
            self._cliente = None
        if (
            self._event_loop and not self._event_loop.is_closed()
        ):  # Check if event loop is not closed before closing.
            self._event_loop.close()
            self._event_loop = None


class APIClientRUS:
    def __init__(self, usuario: str, password: str, codigos: List[str]):
        self._usuario = usuario
        self._password = password
        self.codigos = codigos
        self.ticket: str = None
        self.session: aiohttp.ClientSession = None
        self._is_authenticated = False

    async def __aenter__(self):
        await self.autenticar()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cerrar_sesion()

    @classmethod
    async def create(cls, usuario: str, password: str, codigos: List[str]):
        """Método factory para creación asíncrona"""
        instance = cls(usuario, password, codigos)
        await instance.autenticar()
        return instance

    async def autenticar(self) -> None:
        """Autenticación asíncrona"""
        self.session = aiohttp.ClientSession()
        auth_payload = (
            "<map>"
            "<entry><string>usuario</string><string>{}</string></entry>"
            "<entry><string>password</string><string>{}</string></entry>"
            "</map>"
        ).format(self._usuario, self._password)

        try:
            async with self.session.post(
                "https://sis.rus.com.ar/movil/rest/acceso/validar",
                headers=self._crear_headers_base(),
                data=auth_payload,
            ) as response:
                await self._validar_respuesta(response, "Autenticación")
                data = await response.json()
                self.ticket = data["object"]["ticket"]
                self._is_authenticated = True

        except Exception as e:
            await (
                self.cerrar_sesion()
            )  # Ensure session is closed on authentication failure
            raise

    async def obtener_propuestas(
        self, codigos: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene propuestas para múltiples códigos
        Args:
            codigos: Lista de códigos a consultar (si no se especifica, usa los de la instancia)
        Returns:
            Lista de resultados con estructura [{data: resultados, codigo: codigo}, ...]
        """
        if not self._is_authenticated:
            raise Exception("Sesión no autenticada")

        resultados = []
        codigos_a_procesar = codigos or self.codigos

        for codigo in codigos_a_procesar:
            propuestas_payload = (
                "<map>"
                "<entry><string>productor</string><string>{}</string></entry>"
                "<entry><string>poliza</string><string></string></entry>"
                "<entry><string>socio</string><string></string></entry>"
                "<entry><string>razonSocial</string><string></string></entry>"
                "<entry><string>patente</string><string></string></entry>"
                "<entry><string>propuesta</string><string></string></entry>"
                "<entry><string>fechaCarga</string><string></string></entry>"
                "<entry><string>seccion</string><string></string></entry>"
                "<entry><string>propuestaProrrogaAutomatica</string><string>true</string></entry>"
                "<entry><string>dniOcuit</string><string></string></entry>"
                "<entry><string>tarifaPorUso</string><string></string></entry>"
                "<entry><string>esFlota</string><string>false</string></entry>"
                "</map>"
            ).format(codigo)

            headers = self._crear_headers_base()
            headers.update(
                {
                    "plataforma": "portalpas",
                    "Referer": "https://pas.rus.com.ar/",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                    "ticket": self.ticket,
                }
            )

            try:
                async with self.session.post(
                    "https://sis.rus.com.ar/movil/rest/emision/v2/getPropuestas/",
                    headers=headers,
                    data=propuestas_payload,
                ) as response:
                    await self._validar_respuesta(
                        response, f"Obtención de propuestas para {codigo}"
                    )
                    data = await response.json()

                    resultados.append(
                        {
                            "codigo": codigo,
                            "data": data["object"]["results"],
                            "ticket": self.ticket,
                        }
                    )

            except Exception as e:
                if GLOBAL_DEBUG:
                    print(f"Error en consulta para código {codigo}: {str(e)}")
                continue  # Continue to next code even if one fails

        return resultados

    def generar_XML(self, objeto: dict):
        return f"""
            <map>
                <entry>
                    <string>propuesta</string>
                    <string>{str(objeto.get("propuesta", ""))}</string>
                </entry>
                <entry>
                    <string>renovacion</string>
                    <string>{str(objeto.get("renovacion", ""))}</string>
                </entry>
                <entry>
                    <string>seccion</string>
                    <string>{str(objeto.get("numeroSeccion", ""))}</string>
                </entry>
                <entry>
                    <string>premio</string>
                    <string>{str(objeto.get("premio", ""))}</string>
                </entry>
                <entry>
                    <string>sumaAsegurada</string>
                    <string></string>
                </entry>
                <entry>
                    <string>emitePoliza</string>
                    <string>{str(objeto.get("emitePoliza", True)).lower()}</string>
                </entry>
                <entry>
                    <string>endoso</string>
                    <string>{str(objeto.get("endoso", ""))}</string>
                </entry>
            </map>
        """.strip()

    async def refacturar_propuestas(
        self,
        propuestas: List[Dict[str, Any]],
        datos_refactura: Dict[str, Any] = None,
        callback_refactura=None,
        callback_success=None,
    ):
        """
        Refactura una lista de propuestas.

        Args:
            propuestas (List[Dict[str, Any]]): Lista de propuestas a refacturar.
            datos_refactura (Dict[str, Any], optional): Datos de refactura base. Defaults to None.
            callback_refactura (callable, optional): Función callback para obtener datos de refactura dinámicamente. Defaults to None.

        Returns:
            List[Dict[str, Any]]: Lista de resultados de la refacturación.
        """
        tasks = []
        for prop_data in propuestas:
            if "data" in prop_data and isinstance(prop_data["data"], list):
                for propuesta in prop_data["data"]:
                    task = self.refacturar_propuesta(
                        [propuesta],
                        datos_refactura,
                        callback_refactura=callback_refactura,
                        callback_success=callback_success,
                    )
                    tasks.append(task)
            else:
                if GLOBAL_DEBUG:
                    print(
                        "Error: Formato de propuesta incorrecto. Debe contener 'data' como una lista."
                    )
                return  # Salir si el formato es incorrecto
        # Ejecutar las tareas de forma paralela y esperar los resultados
        results = await asyncio.gather(
            *tasks, return_exceptions=True
        )  # Gather results and also capture exceptions
        for result in results:  # Process results to handle exceptions if any
            if isinstance(result, Exception):
                if GLOBAL_DEBUG:
                    print(f"Error during refactoring a proposal: {result}")
        return results  # Devolver los results, which might contain exceptions

    def calcular_valor_minimo(
        self, precio: float, descuento: float, n_cuotas: int
    ) -> int:
        """
        Calcula el valor mínimo ajustado de forma que las cuotas resultantes sean redondas (múltiplo de 100)
        tras aplicar un descuento a un precio dado.

        Parámetros:
            precio (float): El precio original del producto o servicio.
            descuento (float): El porcentaje de descuento a aplicar sobre el precio.
            n_cuotas (int): El número de cuotas en las que se dividirá el pago.

        Retorna:
            int: El valor mínimo total ajustado. Este valor es mayor o igual al precio con descuento redondeado
                al múltiplo de 100 superior y, además, al dividirlo entre n_cuotas se obtiene un valor que es múltiplo de 100.

        Excepciones:
            ValueError: Si el número de cuotas es menor o igual a 0.
            TypeError: Si el número de cuotas no es un entero.
        """
        if GLOBAL_DEBUG:
            print(precio, descuento, n_cuotas)
        # Validación de parámetros
        if n_cuotas <= 0:
            raise ValueError("El número de cuotas debe ser positivo")
        if not isinstance(n_cuotas, int):
            raise TypeError("El número de cuotas debe ser un entero")

        # Calcular precio con descuento
        precio_con_descuento = precio * (1 - descuento / 100)

        # Redondear el precio con descuento al múltiplo de 100 superior
        redondeado = math.ceil(precio_con_descuento / 100) * 100

        # Para que cada cuota sea redonda (múltiplo de 100), el total debe ser divisible por (n_cuotas * 100).
        # Si no lo es, se ajusta al siguiente múltiplo de (n_cuotas * 100).
        final = None
        if redondeado % (n_cuotas * 100) == 0:
            final = redondeado
        else:
            final = math.ceil(redondeado / (n_cuotas * 100)) * (n_cuotas * 100)
        return final

    async def refacturar_propuesta(
        self,
        propuesta: List[Dict[str, Any]],
        datos_refactura_inicial: Dict[str, Any] = None,
        emitir_poliza: bool = True,
        callback_refactura=None,
        callback_success=None,
    ):
        """
        Refactura una propuesta, intentando múltiples veces si es necesario.

        Args:
            propuesta (List[Dict[str, Any]]): Lista conteniendo la propuesta a refacturar.
            datos_refactura_inicial (Dict[str, Any], optional): Datos de refactura iniciales. Defaults to None.
            callback_refactura (callable, optional): Función callback para obtener datos de refactura dinámicamente. Defaults to None.

        Returns:
            Dict[str, Any]: Diccionario con el resultado de la refacturación y datos de la propuesta.
        """
        if not self._is_authenticated:
            raise Exception("Sesión no autenticada")

        if not propuesta:
            raise ValueError("La propuesta está vacía.")

        # Asegurar que sea un diccionario (toma el primer elemento si es una lista)
        m_propuesta = propuesta[0] if isinstance(propuesta, list) else propuesta

        m_propuesta.setdefault("emitePoliza", emitir_poliza)
        m_propuesta.setdefault("endoso", -1)
        m_propuesta.setdefault("sumaAsegurada", "")

        # Configurar valores por defecto
        datos_refactura = {
            "intervalo": 300,
            "bonificacion": 0,
            **(datos_refactura_inicial or {}),
        }
        if not isinstance(m_propuesta, dict):
            raise TypeError("El formato de propuesta no es válido.")

        max_intentos = 500
        intentos = 0
        m_propuesta["premio"] = self.calcular_valor_minimo(
            m_propuesta["premio"],
            datos_refactura["bonificacion"],
            int(m_propuesta["cantidadCuota"]),
        )

        while True:
            # Obtener datos de refactura usando callback si se proporciona
            if callback_refactura:
                datos_refactura_callback = callback_refactura(
                    {
                        "propuesta": m_propuesta,
                        "datos_refactura": datos_refactura,
                        "intentos": intentos,
                    }
                )
                if datos_refactura_callback:
                    datos_refactura = datos_refactura_callback  # Usar los datos del callback si están disponibles
                    if GLOBAL_DEBUG:
                        print(
                            f"Datos de refactura obtenidos del callback: {datos_refactura}"
                        )
                else:
                    if GLOBAL_DEBUG:
                        print(
                            "Callback no devolvió datos de refactura, usando datos preexistentes o iniciales."
                        )
                    if (
                        not datos_refactura
                    ):  # Si ni siquiera hay datos iniciales y el callback falla
                        return {
                            "success": False,
                            "error": "No se pudieron obtener datos de refactura ni del callback ni iniciales.",
                            "propuesta": m_propuesta,
                        }

            # Calcular el premio con los datos de refactura (ya sea iniciales, preexistentes o del callback)

            try:
                async with self.session.post(
                    "https://sis.rus.com.ar/movil/rest/emision/modificarEndosoProrrogaAutomatica/",
                    headers={
                        "accept": "application/json, text/plain, */*",
                        "accept-language": "es-AR,es;q=0.9,es-ES;q=0.8,en;q=0.7",
                        "content-type": "text/xml",
                        "plataforma": "portalpas",
                        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                        "sec-ch-ua-mobile": "?0",
                        "ua-platform": '"Windows"',
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-site",
                        "ticket": self.ticket,
                        "Referer": "https://pas.rus.com.ar/",
                        "Referrer-Policy": "strict-origin-when-cross-origin",
                    },
                    data=self.generar_XML(m_propuesta),
                ) as response:
                    data = await response.json()
                    if (
                        "recargo que excede el porcentaje permitido"
                        in data["object"]["xml"]
                    ):
                        if GLOBAL_DEBUG:
                            print("El recargo excede el porcentaje permitido")
                        intentos += 1

                        m_propuesta["premio"] = int(
                            int(m_propuesta["premio"])
                            + (int(m_propuesta["cantidadCuota"]) * 100)
                        )

                        if GLOBAL_DEBUG:
                            print(
                                f"Intentos: {intentos}, Premio actual: {m_propuesta['premio']}"
                            )
                        if intentos >= max_intentos:
                            if GLOBAL_DEBUG:
                                print(
                                    "No se pudo refacturar la propuesta después de varios intentos."
                                )
                            return {
                                "success": False,
                                "error": "No se pudo refacturar después de varios intentos",
                                "propuesta": m_propuesta,
                            }  # Return failure and proposal data
                        continue  # Volver a intentar con el premio incrementado
                    else:
                        if GLOBAL_DEBUG:
                            print(
                                f"Póliza refacturada con el premio: {m_propuesta['premio']}"
                            )

                        if callback_success:
                            callback_success(
                                {
                                    "propuesta": m_propuesta,
                                    "datos_refactura": datos_refactura,
                                    "intentos": intentos,
                                }
                            )
                        return {
                            "success": True,
                            "propuesta": m_propuesta,
                        }  # Return success and proposal data

            except Exception as e:
                if (
                    "recargo que excede el porcentaje permitido"
                    in data["object"]["xml"]
                ):
                    if GLOBAL_DEBUG:
                        print("El recargo excede el porcentaje permitido")
                    intentos += 1
                    if datos_refactura:
                        m_propuesta["premio"] = int(
                            int(m_propuesta["premio"])
                            + (int(m_propuesta["cantidadCuota"]) * 100)
                        )
                    else:
                        if GLOBAL_DEBUG:
                            print(
                                "Advertencia: 'intervalo' no definido en datos_refactura. No se incrementará el premio en el reintento."
                            )

                    if GLOBAL_DEBUG:
                        print(
                            f"Intentos: {intentos}, Premio actual: {m_propuesta['premio']}"
                        )
                    if intentos >= max_intentos:
                        if GLOBAL_DEBUG:
                            print(
                                "No se pudo refacturar la propuesta después de varios intentos."
                            )
                        return {
                            "success": False,
                            "error": "No se pudo refacturar después de varios intentos",
                            "propuesta": m_propuesta,
                        }  # Return failure and proposal data
                    continue  # Volver a intentar con el premio incrementado

    async def cerrar_sesion(self) -> None:
        """Cierra la sesión activa y limpia el ticket"""
        if self.session and not self.session.closed:
            await self.session.close()  # Explicitly close the session
            self._is_authenticated = False
            self.ticket = None
            if GLOBAL_DEBUG:
                print("Sesión cerrada correctamente")

    def _crear_headers_base(self) -> Dict[str, str]:
        """Crea headers comunes para todas las solicitudes"""
        return {
            "accept": "application/json, text/plain, */*",
            "accept-language": "es-AR,es;q=0.9,es-ES;q=0.8,en;q=0.7",
            "content-type": "text/xml",
            "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

    async def _validar_respuesta(self, response, operacion: str) -> None:
        """Valida respuestas del servidor"""
        if response.status != 200:
            error = f"Error en {operacion}. Código: {response.status}"
            if GLOBAL_DEBUG:
                print(error)
            await self.cerrar_sesion()  # Close session on non-200 response
            raise Exception(error)

    @property
    def autenticado(self) -> bool:
        """Indica si la sesión está activa"""
        return self._is_authenticated
