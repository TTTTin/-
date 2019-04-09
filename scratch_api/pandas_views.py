import MySQLdb
import pandas as pd
conn = MySQLdb.connect(
    host = '',
    user = '',#一般默认用户名
    passwd = '',#本地数据库登录密码
    db = 'scratchDB',#数据库名称
    port = 3306,#安装mysql默认的端口号
    charset = 'utf8'#设置数据库统一编码
)

#查询点赞数最多作品排行
sql1 = "SELECT scratch_api_production.like,scratch_api_production.name FROM (scratch_api_galleryproduction LEFT JOIN scratch_api_production ON scratch_api_galleryproduction.production_id=scratch_api_production.id) LEFT JOIN scratch_api_user ON scratch_api_production.author_id = scratch_api_user.baseuser_ptr_id WHERE scratch_api_galleryproduction.gallery_id = 'c8d29756ce4d4e72900dcee34b3b6925' AND sex='男' ORDER BY scratch_api_production.like DESC;"
df1 = pd.read_sql(sql1,conn)
#df1
df1.to_json('../static/BigDataAnalysis/查询点赞数最多作品排行.json',orient='table')




#查询结果集中的男女人数

sql2 = "SELECT sex , COUNT(sex) as nums  FROM (scratch_api_galleryproduction LEFT JOIN scratch_api_production ON scratch_api_galleryproduction.production_id=scratch_api_production.id) LEFT JOIN scratch_api_user ON scratch_api_production.author_id = scratch_api_user.baseuser_ptr_id WHERE scratch_api_galleryproduction.gallery_id = 'c8d29756ce4d4e72900dcee34b3b6925' and scratch_api_galleryproduction.admin_checked = 1  AND sex='男' UNION SELECT sex as 性别, COUNT(sex) AS '人数' FROM (scratch_api_galleryproduction LEFT JOIN scratch_api_production ON scratch_api_galleryproduction.production_id=scratch_api_production.id) LEFT JOIN scratch_api_user ON scratch_api_production.author_id = scratch_api_user.baseuser_ptr_id WHERE scratch_api_galleryproduction.gallery_id = 'c8d29756ce4d4e72900dcee34b3b6925' and scratch_api_galleryproduction.admin_checked = 1 AND sex='女';"
df2 = pd.read_sql(sql2,conn)
#df2
df2.to_json('../static/BigDataAnalysis/查询结果集中的男女人数.json',orient='table')



# 查询某专题活动学校参与度排名
sql3 = "SELECT  scratch_api_user.school_id ,COUNT(*) as nums FROM (scratch_api_galleryproduction LEFT JOIN scratch_api_production ON scratch_api_galleryproduction.production_id=scratch_api_production.id) LEFT JOIN scratch_api_user ON scratch_api_production.author_id = scratch_api_user.baseuser_ptr_id WHERE scratch_api_galleryproduction.gallery_id = 'c8d29756ce4d4e72900dcee34b3b6925' and scratch_api_galleryproduction.admin_checked = 1 and scratch_api_user.school_id is not NULL GROUP BY scratch_api_user.school_id order by count(*) desc ;"
df3 = pd.read_sql(sql3,conn)
#df3
df3.to_json('../static/BigDataAnalysis/查询某专题活动学校参与度排名.json',orient='table')
# df3.to_json('/Users/pailiu/Downloads/查询某专题活动学校参与度排名.json',orient='table')



# 查询查询年级占比
sql4 = "SELECT  scratch_api_user.grade ,COUNT(*)  as  nums FROM (scratch_api_galleryproduction LEFT JOIN scratch_api_production ON scratch_api_galleryproduction.production_id=scratch_api_production.id) LEFT JOIN scratch_api_user ON scratch_api_production.author_id = scratch_api_user.baseuser_ptr_id WHERE scratch_api_galleryproduction.gallery_id = 'c8d29756ce4d4e72900dcee34b3b6925' and scratch_api_galleryproduction.admin_checked = 1 and scratch_api_user.grade is not NULL GROUP BY scratch_api_user.grade order by count(*) desc;"
df4 = pd.read_sql(sql4,conn)
df4
df4.to_json('../static/BigDataAnalysis/查询查询年级占比.json',orient='table')
# df4.to_json('/Users/pailiu/Downloads/查询查询年级占比.json',orient='table')


# 查询学校占比
sql5 = "SELECT  scratch_api_user.school_id ,COUNT(*) as nums FROM (scratch_api_galleryproduction LEFT JOIN scratch_api_production ON scratch_api_galleryproduction.production_id=scratch_api_production.id) LEFT JOIN scratch_api_user ON scratch_api_production.author_id = scratch_api_user.baseuser_ptr_id WHERE scratch_api_galleryproduction.gallery_id = 'c8d29756ce4d4e72900dcee34b3b6925' and scratch_api_galleryproduction.admin_checked = 1 and scratch_api_user.school_id is not NULL GROUP BY scratch_api_user.school_id order by count(*) desc;"
df5 = pd.read_sql(sql5,conn)
df5
df5.to_json('../static/BigDataAnalysis/查询学校占比.json',orient='table')
# df5.to_json('/Users/pailiu/Downloads/查询学校占比.json',orient='table')


# 查询作品提交时间
sql6 = "SELECT  DATE_FORMAT(scratch_api_production.update_time,\"%Y/%m/%e\") as 'date',count(*) as 'nums' FROM (scratch_api_galleryproduction LEFT JOIN scratch_api_production ON scratch_api_galleryproduction.production_id=scratch_api_production.id) LEFT JOIN scratch_api_user ON scratch_api_production.author_id = scratch_api_user.baseuser_ptr_id WHERE scratch_api_galleryproduction.gallery_id = 'c8d29756ce4d4e72900dcee34b3b6925' and scratch_api_galleryproduction.admin_checked = 1 GROUP BY DATE_FORMAT(scratch_api_production.update_time,\"%Y/%m/%e\");"
df6 = pd.read_sql(sql6,conn)
#df6
df6.to_json('../static/BigDataAnalysis/查询作品提交时间.json',orient='table')
# df6.to_json('/Users/pailiu/Downloads/查询作品提交时间.json',orient='table')



conn.close()