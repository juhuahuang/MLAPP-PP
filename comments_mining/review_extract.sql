 # comments from renter to owner and car
 select r.orderID,r.carID, r.`comment` from order_reviews r join
 (select carID,count(carID) n from order_reviews  GROUP BY carID) tmp on
 r.carID = tmp.carID and tmp.n>50
 
 #comments from owner to renter

 select r.orderID, r.renterID,r.`comment` from renter_reviews r join 
 (select renterID ,count(renterID) n from renter_reviews  GROUP BY renterID) tmp on
 r.renterID = tmp.renterID and tmp.n>15 where length(r.`comment`) > 24