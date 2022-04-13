import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class Brix(scrapy.Spider):
    name = "brix"
    custom_settings = {
        "DOWNLOAD_DELAY": 0
    }

    def __init__(self):
        super().__init__()
        self.supplier = "JS%20ASAKASHI"
        self.i = 0

    def start_requests(self):
        yield scrapy.Request("https://brixogroup.com/catalog/api/vehicle/brand", callback=self.parse_urls,
                             meta={
                                 "level": "brands"
                             })

    def parse_urls(self, response):
        level = response.meta.get("level")

        if level == "brands":
            brands = json.loads(response.text)

            print(brands)

            for brand in brands["result"]:
                if brand["name"] != "AUDI":
                    continue
                brand_id = brand['id']

                yield scrapy.Request(
                    f"https://brixogroup.com/catalog/api/vehicle/brand/{brand_id}/model?carBrand={brand_id}",
                    callback=self.parse_urls, meta={
                        "level": "models",
                    })
        elif level == "models":
            models = json.loads(response.text)
            print(models)

            for model in models["result"]:
                for vehicle in model["vehicles"]:
                    vehicle_id = vehicle["id"]

                    yield scrapy.Request(
                        f"https://brixogroup.com/catalog/api/article/by-vehicle/{vehicle_id}?supplier={self.supplier}",
                        callback=self.parse_urls, meta={
                            "level": "vehicles",
                        })
        elif level == "vehicles":
            vehicles = json.loads(response.text)
            print(vehicles)

            # for vehicle in vehicles["result"]["articles"]:
            #     url = f"https://brixogroup.com/catalog/part/{vehicle['id']}"
            #     print(url)
            #     yield scrapy.Request(url,
            #                          callback=self.parse_item,
            #                          meta={"level": "item", "id": vehicle['id'], "url": url,
            #                                "article": vehicle["articleNumber"], "chars": vehicle["attributes"]})

    def parse_item(self, response):
        level = response.meta.get("level")

        if level == "item":
            item_name = " ".join(response.xpath("//h1[@class='page-part__title']//text()").getall())

            #names = response.xpath("//div[@class='part-properties__name']/text()").getall()
            #values = response.xpath("//div[@class='part-properties__value part-properties__value--large']/text() |"
            #                        "//div[@class='part-properties__value']/text()").getall()

            #if len(names) != len(values):
            #    raise ValueError("ERROR names != values!!!!!!!")

            characteristics = {}
            #for name, value in zip(names, values):
            #    characteristics.update({name: value})

            chars = response.meta.get("chars")
            for ch in chars:
                characteristics.update({ch["key"]: ch["value"]})

            compatibles = []
            compatible = response.xpath("//tr[@class='grid__body-row grid__body-row--pointer']//text()").getall()
            for i in range(0, len(compatible), 4):
                tmp_comp = compatible[i:i+4]
                tmp_comp.pop(2)
                compatibles.append(tmp_comp)

            #article = response.xpath("//span[@class='page-part__part-code']/text()").getall()[1]
            article = response.meta.get("article")

            id_ = response.meta.get("id")

            result = {
                "url": response.meta.get("url"),
                "article": article,
                "name": item_name,
                "compatibles": compatibles,
                "characteristics": characteristics,
                "id": id_
            }

            yield scrapy.Request(f"https://brixogroup.com/catalog/api/article/by-id/{id_}?id={id_}",
                                 meta={"level": "oem", "result": result}, callback=self.parse_item)
        elif level == "oem":
            result = response.meta.get("result")

            manufacturers = json.loads(response.text)["result"]["manufacturers"]
            oem = []

            for m in manufacturers[0:6]:
                oem.append(m["oemNumber"])

            result.update({"oem": oem})

            yield result


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())

    process.crawl('brix')
    process.start()









