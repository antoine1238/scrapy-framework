autopep8 > sirve para formatear nuestro código de manera eficiente siguiendo la guia de estilos de python 

Comandos Básicos:
    -scrapy startproject <name>                       > para crear el proyecto
    -scrapy shell <"url">                             > para abrir la consola interactiva usando la url de la pag. como base 
    -scrapy crawl <variable name de la clase spider>            > ejecuta el scripts de scrapy
    -scrapy crawl <v. s.> -o <nombre_archivo.(json, csv, ect)>  > ejecuta el scripts de scrapy y lo guarda en un archivo que especifiquemos.


Estructura de scrapy:
    *name_proyect
        *name_proyect
            *spider
            -items.py
            -middlewares.py
            -pipelines.py
            -settings.py
        -scrapy.cfg

- Folder-spiders: en donde se crearán los scripts.
- items.py: transforma los datos que se reciben del requests.
- middlewares.py: trabaja con un concepto denominado señales: controla eventos que suceden entre los requests y la captura de información
- pipelines.py: permite modificar los datos desde que entran al spider (scripts que extraen información) hasta el final.
- settings.py: archivo con configuraciones del uso de Scrapy.
- scrapy.cfg Contiene la informacion para el deply



clase Spider:
    En palabras sencillas es una clase de Python (Scrapy) en la que definimos la lógica necesaria para extraer informacion. 
    es una clase a la cual le decimos que informacion queremos, que informacion no queremos y como guardar esa informacion.

    Esta recibe las variables:
    
    name = nombre único al que se hará referencia al momento de ejecutar nuestro script.
    start_urls = urls que vamos a consultar. nuestro proyecto visitará cada una de ellas 
    custom_settings = {                    
        "FEED_URI": "N_archivo.json",    > define nombre del archivo en donde se guardarán los datos
        "FEED_FORMAT": "json",           > formato del archivo
        "CONCURRENT_REQUESTS: 24,        > al ser un framework asincrono, esto limita las tareas simultaneas
        "MEMUSAGE_LIMIT_MB": 2048,       > limita el uso de memoria RAM     
        "MEMUSAGE_NOTIFY_MAIL": ["@"],   > de superarse el uso de memoria RAM, este enviará un mensaje al email especificado
        "ROBOTSTXT_OBEY": True,          > para que obedesca las limitaciones del robots.txt de la pagina
        "USER_AGENT": "antoine"          > cuando ejecutemos el spider, podemos definir nuestro nombre para dar información al servidor
        "FEED_EXPORT_ENCODING": "utf-8"  > enconding de los datos
    }

    Funcion a sobreescribir obligatoriamente:
        Parse: 
            esta recibe la respuesta y con ello podemos analizar y traer el contenido de la url indicada
            aqui por ejemplo obtenemos los datos y su posterior guardado en un nuevo archivo.
            esta recibe un parametro llamado "response" el cual dentro tiene toda la informacion que se obtuvo de las urls 
            que definimos en "start_urls".

        Ejemplo: 
            def parse(self, response):
                with open("archivo.txt", "w") as f:
                    f.write(response.text)


    Guardado de datos en archivo:
        dentro de la funcion parse, tenemos que retornar los datos y guardarlos en un archivo. para retornarlo usamos 
        el retorno 'yield'(para no terminar con la funcion) en el cual pondremos los datos dentro de un diccionario.. 
        despues ejecutamos en nuestra base del proyecto el comando ' scrapy crawl <N_spider> -o <N_archivo>.json '
        .. podemos guardar tambien en formato csv.

            Ejemplo:
                def parse(self, response):
                    titulo = response.xpath("//div[@class='col-md-8']/h1/a/text()").get()
                    tags = response.xpath("//div[contains(@class, 'tags-box')]//a[contains(@class, 'tag')]/text()").getall()
                    frases = response.xpath("//div[@class='col-md-8']/div[@class='quote']/span[@class='text']/text()").getall()
                    link_next = response.xpath("//li[@class='next']/a/@href").get()

                    yield {
                            "titulo": titulo,
                            "tags": tags,
                            "frases": frases
                        }

                    more code...

        Si vuelvo a ejecutar el comando anterior ya existiendo ese archivo lo que realizara scrapy es un append 
        al archivo existente, para solucionar este problema y no tener datos duplicados unicamente debo borrar 
        el archivo antes de ejecutar el comando.

        igual podemos definir la variable 'custom_settings' para darle el archivo y formato que queremos que se guarde 
        cada vez que ejecutemos 

    Callbacks: para seguir obteniendo datos de otros links de la página
    
        cuando terminamos de obtener los datos usando yield, la funcion no para, si no que si ejecuta el codigo siguiente
        que tengamos escrito. si quiero obtener los datos de otras paginas solo tengo que obtener el link del boton 'next' 
        y en el caso de que exista 'if' retornar yield nuevamente pero esta vez usando 'response.follow()' el cual recibe 
        dos parametros.. el link obtenido con xpath y el callback el cual es una variable que recibe la funcion que 
        quieres ejecutar.
        
        esto hará que obtengamos los datos, sigamos el link y volvamos a obtener los datos hasta que no haya mas páginas

            yield response.follow(link_next, callback=self.parse)

        Callbacks con otras funciones parse:
            con response.follow podemos llamar a otra funcion que haga otra lógica que querramos. follow puede enviar datos 
            mediante el uso de un diccionario, en la funcion nueva sólo tendiramos que recibir esos datos usando el 
            parametro **kwargs.

            En este ejemplo hice que la funcion 'parse_quotes' recibiera un diccionario que contenia los datos de la primera
            pagina y dentro definí una variable que encapsule esos datos, luego con el metodo 'extend' pude agregar los
            nuevos datos al diccionarion como si se tratase de un append. luego verifique que hubiera un boton next al igual
            que hice con la funcion parse, solo que este se vuelve a llamar a sí misma hasta que no haya mas el boton, 
            en cuyo caso retorno con yield los datos para ser guardados por scrapy

            Código:
                def parse_quotes(self, response, **kwargs):
                    if kwargs:
                        citas = kwargs['citas']
                    citas.extend(response.xpath(                     # añade datos al diccionario como un append
                        "//div[@class='col-md-8']/div[@class='quote']/span[@class='text']/text()"   
                    ).getall()) 
                    
                    link_next = response.xpath("//li[@class='next']/a/@href").get()
                    if link_next:  # si aún hay el boton next, seguirá obteniendo datos llamandose otra vez
                        yield response.follow(link_next, callback=self.parse_quotes, cb_kwargs={'citas':citas}) 
                        
                    else:          # si ya no esta el boton next, entonces retorna todos los datos obtenidos para que se guarden 
                        yield {
                            'citas': citas    
                        }

                def parse(self, response):
                    titulo = response.xpath("//div[@class='col-md-8']/h1/a/text()").get()
                    tags = response.xpath("//div[contains(@class, 'tags-box')]//a[contains(@class, 'tag')]/text()").getall()
                    citas = response.xpath("//div[@class='col-md-8']/div[@class='quote']/span[@class='text']/text()").getall()

                    yield {
                        "titulo": titulo,
                        "tags": tags
                    }

                    link_next = response.xpath("//li[@class='next']/a/@href").get()
                    if link_next:
                        yield response.follow(link_next, callback=self.parse_quotes, cb_kwargs={'citas':citas})



Scrapy shell: 
    dentro podemos jugar con los datos y mas cosas de la url que asignamos. 
    
    Request: 
        request.body            
        request.method
        request.headers
        request.encoding
        request.status
        request.follow(link, callback=self.parse, cb_kwargs={'mensaje':mensaje}) 
        > este ultimo Recibe dos parametros obligatorios el link que obtuvimos con xpath y la funcion que se va a ejecutar
          tambien puede enviar datos como contexto usando la variable cb_kwargs como diccionario.

    Response: para navegar por los contenidos del html usando xpath
        response.xpath("//h1/a/text()").get()                                                             > titulo
        response.xpath("//div/span[@class='text' and @itemprop='text']").getall()                         > frases
        response.xpath("//div[contains(@class, 'tags-box')]//a[contains(@class, 'tag')]/text()").getall() > generos
        response.xpath("//div[@class='quote']/span/small/text()").getall()                                > autores


    Metodos dentro del xpath:
        div[@class='', @id='', @href='']    > obtiene la etiqueta selecionada según cumpla el filtro de sus atributos
        div[contains(@class, "tags")]       > contains: recibe el atributo a filtrar y el valor del mismo.
        text()                              > para sacar el texto de la etiqueta. va acompañado de get() o getall() al final
        .get()                              > para obtener un dato de una etiqueta
        .getall()                           > para obtener los datos de varias etiquetas

