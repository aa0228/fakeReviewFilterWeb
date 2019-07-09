# coding: utf-8
from sqlalchemy import (Column, DateTime, Float, ForeignKey,
                        Integer, String, Text, text)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class CheckExistsInterface():
    def checkExists(self, session):
        cls = type(self)
        return session.query(cls).filter(cls.id == self.id).count() > 0


class Product(Base, CheckExistsInterface):
    __tablename__ = 'product'

    id = Column(String(50, 'utf8mb4_unicode_ci'), primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    price = Column(Float(asdecimal=True), nullable=False)
    productTypeId = Column(ForeignKey('productType.id'), nullable=False,
                           index=True)

    productType = relationship('ProductType')

    def __str__(self):
        return '<product id={}, name={}, price={}, productTypeId={}>'.\
            format(self.id, self.name, self.price, self.productTypeId)


class ProductType(Base, CheckExistsInterface):
    __tablename__ = 'productType'

    id = Column(Integer, primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)

    def __str__(self):
        return '<ProductType id={}, name={}>'.format(self.id, self.name)


class Review(Base, CheckExistsInterface):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    productTypeId = Column(ForeignKey('productType.id'),
                           nullable=False, index=True)
    productId = Column(ForeignKey('product.id'), nullable=False, index=True)
    reviewUserId = Column(ForeignKey('reviewUser.id'),
                          nullable=False, index=True)
    reviewUsefulCount = Column(Integer, nullable=False)
    reviewVotedTotalCount = Column(Integer, nullable=False)
    reviewScore = Column(Float(asdecimal=True), nullable=False)
    reviewTime = Column(DateTime, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP ON\
                        UPDATE CURRENT_TIMESTAMP"))
    reviewSummary = Column(Text(collation='utf8mb4_unicode_ci'),
                           nullable=False)
    reviewContent = Column(Text(collation='utf8mb4_unicode_ci'),
                           nullable=False)

    product = relationship('Product')
    productType = relationship('ProductType')
    reviewUser = relationship('ReviewUser')

    def __str__(self):
        return ('<review id={}, productTypeId={}, productId={}, reviewUserId={},\
        reviewUsefulCount={}, reviewVotedTotalCount={}, reviewScore={},\
         reviewTime={},\
        reviewSummary={}, reviewContent={}>'.
                format(self.id, self.productTypeId,
                       self.productId, self.reviewUserId,
                       self.reviewUsefulCount, self.reviewVotedTotalCount,
                       self.reviewScore, self.reviewTime, self.reviewSummary,
                       self.reviewContent))

    def checkExists(self, session):
        return (session.query(Review.id).
                filter(Review.reviewUserId == self.reviewUserId and
                       Review.productId == self.productId and
                       Review.reviewTime == self.reviewTime and
                       Review.reviewContent == self.reviewContent).count() > 0)


class ReviewUser(Base, CheckExistsInterface):
    __tablename__ = 'reviewUser'

    id = Column(String(50, 'utf8mb4_unicode_ci'), primary_key=True)
    name = Column(String(255, 'utf8mb4_unicode_ci'), nullable=False)

    def __str__(self):
        return '<user id={} name={}>'.format(self.id, self.name)


class TextAnalysisMaxSRecord(Base):
    __tablename__ = 'textAnalysisMaxSRecord'

    id = Column(Integer, primary_key=True)
    productTypeId = Column(ForeignKey('productType.id'),
                           nullable=False, index=True)
    maxS = Column(Float(asdecimal=True), nullable=False)

    productType = relationship('ProductType')
