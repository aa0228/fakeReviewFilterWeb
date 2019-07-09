# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


t_argsOfProductType = Table(
    'argsOfProductType', metadata,
    Column('productTypeId', ForeignKey('productType.id'), nullable=False, unique=True),
    Column('scoreRatio', Float(asdecimal=True), nullable=False),
    Column('textRatio', Float(asdecimal=True), nullable=False),
    Column('emotionRatio', Float(asdecimal=True), nullable=False)
)


class Product(Base):
    __tablename__ = 'product'

    id = Column(String(50, 'utf8mb4_unicode_ci'), primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    price = Column(Float(asdecimal=True), nullable=False)
    productTypeId = Column(ForeignKey('productType.id'), nullable=False, index=True)

    productType = relationship('ProductType')


class ProductType(Base):
    __tablename__ = 'productType'

    id = Column(Integer, primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)


class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    productTypeId = Column(ForeignKey('productType.id'), nullable=False, index=True)
    productId = Column(ForeignKey('product.id'), nullable=False, index=True)
    reviewUserId = Column(ForeignKey('reviewUser.id'), nullable=False, index=True)
    reviewUsefulCount = Column(Integer, nullable=False)
    reviewVotedTotalCount = Column(Integer, nullable=False)
    reviewScore = Column(Float(asdecimal=True), nullable=False)
    reviewTime = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    reviewSummary = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)
    reviewContent = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)

    product = relationship('Product')
    productType = relationship('ProductType')
    reviewUser = relationship('ReviewUser')


class ReviewUser(Base):
    __tablename__ = 'reviewUser'

    id = Column(String(50, 'utf8mb4_unicode_ci'), primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)


class TextAnalysisMaxSRecord(Base):
    __tablename__ = 'textAnalysisMaxSRecord'

    id = Column(Integer, primary_key=True)
    productTypeId = Column(ForeignKey('productType.id'), nullable=False, index=True)
    maxS = Column(Float(asdecimal=True), nullable=False)

    productType = relationship('ProductType')
