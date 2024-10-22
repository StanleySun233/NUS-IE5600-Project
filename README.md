# 查询轨迹数量大于1000的船

```sql
select *
from ais
where MMSI in
      (select MMSI
       from ais
       group by MMSI
       having count(MMSI) >= 1000
    limit 100
    )
order by MMSI
```

使用django生成一个管理系统，对数据库data.db的ais表和ship进行增删改查。查询使用分页，一页50个数据。
create table ais
(
id INTEGER,
mmsi TEXT,
ts TEXT,
lon REAL,
lat REAL,
speed REAL,
heading REAL
);
create table ship
(
id integer,
mmsi integer
);
实现以下功能：

1. 主页显示