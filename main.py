from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import SessionLocal, engine
import database_model
from sqlalchemy.orm import Session


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

database_model.Base.metadata.create_all(bind=engine)

@app.get("/")

def greet():
    return "Welcome"

products = [
    Product(id=1,name="iphone 17 pro",description="apple phone",price=1000.0,quantity=5),
    Product(id=2,name="Samsung Galaxy S24",description="android phone",price=800.0,quantity=10),
    Product(id=3,name="Google Pixel 8",description="android phone",price=700.0,quantity=8),
    Product(id=4,name="OnePlus 11",description="android phone",price=600.0,quantity=12)
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = SessionLocal()

    count = db.query(database_model.Product).count
    if count == 0 :
        for product in products:
            db.add(database_model.Product(**product.model_dump()))

        db.commit()

init_db()

#db connection
#db querry
@app.get("/products/")
def get_all_products(db : Session = Depends(get_db)):
    db_products = db.query(database_model.Product).all()
    return db_products

@app.get("/products/{product_id}")
def get_product(product_id : int , db : Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if db_product:
        return db_product
    return "no product found"

@app.post("/products/")
def add_product(product : Product, db : Session = Depends(get_db)):
    new_product = database_model.Product(**product.model_dump())

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
    except Exception as e:
        db.rollback()
        
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT, 
            detail="Error adding product to the database : " + str(e)
        )
    
    return new_product

@app.delete("/products/{product_id}")
def delete_product(product_id : int, db : Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "product deleted successfully"
    return "no product with matching id"

@app.put("/products/{product_id}")
def update_product(product_id : int, updated_product : Product, db : Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if db_product:
        for key, value in updated_product.model_dump().items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        return "product updated successfully : " + str(db_product)
    else :
        return "no product with matching id"