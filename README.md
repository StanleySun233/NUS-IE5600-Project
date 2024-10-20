# 查询轨迹数量大于1000的船
```sql
select *
from
ais
where MMSI in
(
    select MMSI
    from ais
    group by MMSI
    having count(MMSI) >= 1000
    limit 100
)
order by MMSI
```