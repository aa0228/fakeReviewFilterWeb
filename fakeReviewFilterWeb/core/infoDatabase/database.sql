drop database if exists amazon;
create database amazon;
use amazon;


create table productType (
id int primary key auto_increment,
name varchar(255) not null
);

create table argsOfProductType(
productTypeId int unique not null,
scoreRatio double not null,
textRatio double not null,
emotionRatio double not null,
threshold double not null,
foreign key(productTypeId) references productType(id)
);

create table textAnalysisMaxSRecord (
id int primary key auto_increment,
productTypeId int not null,
maxS double not null,
foreign key(productTypeId) references productType(id)
);

create table product (
id char(50) primary key,
name char(255) not null,
price double not null,
productTypeId int not null,
foreign key(productTypeId) references productType(id)
);

create table reviewUser (
id char(50) primary key,
name char(255) not null
);

create table review (
id int primary key auto_increment,
productTypeId int not null,
productId char(50) not null,
reviewUserId char(50) not null,
reviewUsefulCount int not null,
reviewVotedTotalCount int not null,
reviewScore double not null,
reviewTime timestamp not null,
reviewSummary text not null,
reviewContent text not null,
foreign key(productTypeId) references productType(id),
foreign key(productId) references product(id),
foreign key(reviewUserId) references reviewUser(id)
);
