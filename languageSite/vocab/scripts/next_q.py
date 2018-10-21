	
from django.db import connection	


def run():
	q = "select exp.id as exp_id, scr.id as scr_id, exp.frequency as freq, ifnull(scr.successcount/scr.attempts * exp.frequency, 0.5)  as factor from vocab_expression as exp left outer join vocab_aggrscore as scr on scr.expression_id = exp.id order by factor * rand()";
	crs = connection.cursor()
	crs.execute(q)
	print(crs.fetchall())