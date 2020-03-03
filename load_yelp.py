import json
import psycopg2
conn=psycopg2.connect(database="yelp",user="postgres",password="8762",host="localhost",port="5432")
cur=conn.cursor()

# cur.execute(
#             'CREATE TABLE Photo('
#             'photo_id TEXT,'
#             'business_id  TEXT,'
#             'label TEXT,'
#             'PRIMARY KEY(photo_id)'
#             ')'
#         )

def get_data():
    file = open('yelp_dataset/photo.json', 'r', encoding = 'utf-8')
    camera_text = []
    for line in file.readlines():
        data = json.loads(line)  # 解析每一行数据
        camera_text.append(data) 
    print(len(camera_text))
    return camera_text
 
def data_insert(camera_text):
    for i in range(0,len(camera_text)):
        cur.execute("INSERT INTO Photo VALUES('%s','%s','%s')"%(list(camera_text[i].values())[1],\
                                                                      list(camera_text[i].values())[2],\
                                                                      list(camera_text[i].values())[3]))
# a=get_data()
# data_insert(a)
# conn.commit()
# cur.close()
# conn.close()

cur.execute(
            'CREATE TABLE Business('
            'business_id TEXT,'
            'name TEXT,'
            'city TEXT,'
            'stars FLOAT,'
            'review_count INTEGER,'
            'parking INTEGER,'
            'credit_card INTEGER,'
            'price_range INTEGER,'
            'good_for_groups INTEGER,'
            'good_for_kids INTEGER,'
            'noise_level TEXT,'
            'reservation INTEGER,'
            'PRIMARY KEY(business_id)'
            ')'
        )
conn.commit()

def get_business_data():
    file = open('yelp_dataset/business.json', 'r', encoding = 'utf-8')
    business_text = []
    for line in file.readlines():
        data = json.loads(line) 
        business_text.append(data) 

    return business_text

def cleanString(string):
        return string.strip().replace("'", "''").replace('\n', '')

def business_data_insert(business_text):
    for i in range(len(business_text)):
        info = business_text[i]
        business_id = cleanString(info["business_id"]) 
        name = cleanString(info["name"])
        city = cleanString(info["city"]) 
        stars = info["stars"]
        review_count = info["review_count"]
        attrs = info["attributes"]
        if attrs: 
            if "BusinessParking" in attrs:
                parking = 1
            else:
                parking = 0
            if "BusinessAcceptsCreditCards" in attrs:
                credit_card = 1
            else:
                credit_card = 0
            if "RestaurantsPriceRange2" in attrs:
                if attrs["RestaurantsPriceRange2"] != 'None':
                    price_range = int(attrs["RestaurantsPriceRange2"]) 
            else:
                price_range = 0
            if "RestaurantsGoodForGroups" in attrs:
                good_for_groups = int(attrs["RestaurantsGoodForGroups"] == 'True')
            else:
                good_for_groups = 0
            if "GoodForKids" in attrs:
                good_for_kids = int(attrs["GoodForKids"] == 'True')
            else:
                good_for_kids = 0
            if "NoiseLevel" in attrs:
                if attrs["NoiseLevel"] != 'None':
                    noise_level = cleanString(attrs["NoiseLevel"])
            else:
                noise_level = ""
            if "RestaurantsReservations" in attrs:
                reservation = int(attrs["RestaurantsReservations"] == "True")
            else:
                reservation = 0

        cur.execute("INSERT INTO business VALUES ('%s', '%s', '%s', '%f', '%d','%d','%d','%d','%d','%d', '%s', '%d' )" % \
            (business_id, name, city, stars, review_count, parking, \
                credit_card, price_range, good_for_groups, good_for_kids, noise_level, reservation))

b = get_business_data()
business_data_insert(b)
conn.commit()
cur.close()
conn.close()