import requests
import urllib.parse
from hashlib import sha256
from hmac import HMAC
import datetime

userid_source =  input("Enter Source Jumia User ID: ")
key_source = input("Enter Source Jumia API Key: ")
products_filter = input("Enter Products Filter (all, live, inactive, deleted, image-missing, pending, rejected, sold-out): ")
userid_dest = input("Enter Destination Jumia User ID: ")
key_dest = input("Enter Destination Jumia API Key: ")

def get_endpoint(userid, key, action):
    parameters = {
                'UserID': userid,
                'Version': '1.0',
                'Action': action,
                'Format':'JSON',
                'Timestamp': datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    }
    api_key = key.encode(encoding='utf-8')
    concatenated = urllib.parse.urlencode(sorted(parameters.items())).encode(encoding='utf-8')
    return f"https://sellercenter-api.jumia.ma?{concatenated.decode()}&Signature={HMAC(api_key, concatenated, sha256).hexdigest()}"

def get_products():
    data = requests.get(get_endpoint(userid_source, key_source, "GetProducts")).json()
    products = data["SuccessResponse"]["Body"]["Products"]["Product"]
    return products

def post_products():
    data = requests.get(get_endpoint(userid_dest, key_dest, "ProductCreate")).json()
    for product in get_products():
        data = f"""
<?xml version="1.0" encoding="UTF-8" ?>
<Request>
<Product>
<Brand>{product["Brand"]}</Brand>
<Description>{product["Description"]}</Description>
<Name>{product["Name"]}</Name>
<Price>{product["Price"]}</Price>
<PrimaryCategory>{product["PrimaryCategory"]}</PrimaryCategory>
<Categories>2,3,5</Categories>
<SellerSku>{product["SellerSku"]}</SellerSku>
<TaxClass>{product["TaxClass"]}</TaxClass>
</Product>
</Request>"""
        image = f"""
<?xml version="1.0" encoding="UTF-8" ?>
<Request>
<ProductImage>
<SellerSku>{product["SellerSku"]}</SellerSku>
<Images>
<Image>http://www.rocket-internet.de/sites/default/files/header_bg_imgs/map_home.jpg</Image>
</Images>
</ProductImage>
</Request>"""
        print(data + image)
        c = input("Add product ? (Y/N): ")
        if c in ["Y","y"]:
            requests.post(url=get_endpoint(userid_dest, key_dest, "ProductCreate"), data=data)
            requests.post(url=get_endpoint(userid_dest, key_dest, "ProductImage"), data=image)

post_products()
    
