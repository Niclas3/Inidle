-- User table
-- create database inidle;
use inidle;
 create table Users
 (
     user_id           int         not null AUTO_INCREMENT,
     user_name         varchar(15) null ,
     user_pass         varchar(15) null ,
     user_icon         MEDIUMBLOB  null ,
     user_isdel        boolean     not null  default 0,
     user_delTime      datetime    null,
     user_friendsNum   int         not null  default 0,
     user_friendsNames text      null ,
 
     primary key (user_id)
 ) ENGINE=InnoDB;

 Plans table
 create table Plans
 (
     plan_id           int         not null AUTO_INCREMENT,
     plan_userId       int         not null,
     plan_classId      int         not null,
     plan_monthvector  int         null,
     plan_dayvector    int         null,
     plan_gemTime      datetime    null,
 
     primary key (plan_id),
     foreign key (plan_userId)  
     references Users (user_id)
 
 )ENGINE=InnoDB;

 config table
create table Config
(
    config_id         int         not null  AUTO_INCREMENT,
    config_userid     int         not null,
    is_visible        boolean     null     default 0,

    primary key (config_id),
    foreign key (config_userid)  references Users (user_id)
)ENGINE=InnoDB;
