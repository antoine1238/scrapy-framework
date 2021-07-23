import scrapy

# variables xpath
# tags = "//div[contains(@class, 'tags-box')]//a[contains(@class, 'tag')]/text()"
# titulo = "//div[@class='col-md-8']/h1/a/text()"
# frases = "//div[@class='col-md-8']/div[@class='quote']/span[@class='text']/text()"
# link_next = "//li[@class='next']/a/@href"
# autores = "//div[@class='quote']/span/small/text()"


class QuoteScrapy(scrapy.Spider):
    name = "quotes"         # nombre único
    start_urls = [          # urls
        "https://quotes.toscrape.com/page/1/"
    ]
    custom_settings = {             # configuracion
        "FEED_URI": "datos_quotes.json",
        "FEED_FORMAT": "json",  
        "CONCURRENT_REQUESTS": 24,          # al ser un framework asincrono, esto limita las tareas simultaneas
        "MEMUSAGE_LIMIT_MB": 2048,          # limita el uso de memoria RAM     
        "MEMUSAGE_NOTIFY_MAIL": ["@"],      # de superarse el uso de memoria RAM, este enviará un mensaje al email especificado
        "ROBOTSTXT_OBEY": True,             # para que obedesca las limitaciones del robots.txt de la pagina
        "USER_AGENT": "antoine",            # cuando ejecutemos el spider, podemos definir nuestro nombre para dar información al servidor
        "FEED_EXPORT_ENCODING": "utf-8"     # encoding de los datos 
    }

    def parse_quotes(self, response, **kwargs):
        if kwargs:
            citas = kwargs['citas']
            autores = kwargs['autores']
        citas.extend(response.xpath("//div[@class='col-md-8']/div[@class='quote']/span[@class='text']/text()").getall())   # añade datos al diccionario como un append
        autores.extend(response.xpath("//div[@class='quote']/span/small/text()").getall())  
        
        link_next = response.xpath("//li[@class='next']/a/@href").get()
        if link_next:
            yield response.follow(link_next, callback=self.parse_quotes, cb_kwargs={'citas':citas, 'autores': autores})    # si aún hay el boton next, seguirá obteniendo datos llamandose otra vez
        else: 
            citas_autores = []
            for i in range(len(citas)):
                citas_autores.append(f"{autores[i]} - {citas[i]}")
            yield {
                'citas': citas_autores           # si ya no esta el boton next, entonces retorna todos los datos obtenidos para que se guarden 
            }

    def parse(self, response):
        titulo = response.xpath("//div[@class='col-md-8']/h1/a/text()").get()
        tags = response.xpath("//div[contains(@class, 'tags-box')]//a[contains(@class, 'tag')]/text()").getall()
        citas = response.xpath("//div[@class='col-md-8']/div[@class='quote']/span[@class='text']/text()").getall()
        autores = response.xpath("//div[@class='quote']/span/small/text()").getall() 

        top = getattr(self, 'top', None)  # getattr busca el atributo top, si no lo encuentra, es None # esto es para limitar el numero de tags que quiero que me traiga. 
        if top:                           # para pasar el atributo lo hacemos con la consola al momento de ejecutar scrapy ' scrapy crawl quotes -a top=4 '
            top = int(top)
            tags = tags[:top]

        yield {                 # retorno de datos para su guardado 
            "titulo": titulo,
            "tags": tags
        }

        link_next = response.xpath("//li[@class='next']/a/@href").get()
        if link_next:
            yield response.follow(link_next, callback=self.parse_quotes, cb_kwargs={'citas':citas, "autores":autores})