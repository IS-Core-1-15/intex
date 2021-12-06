from django.db import connection

# Who is currently prescribing high levels of opioids (compared to other non-opioid drugs)?


def query1():
    hundred = '''
    select t2.Prescriber, t2.OpioidPortionOfPrescriptions
from (
	SELECT t1.Prescriber, CONCAT(t1.OpioidPortionOfPrescriptions, '%') as OpioidPortionOfPrescriptions
	FROM (SELECT CONCAT(p.lname, ', ', p.fname) AS Prescriber, 
				round((((COALESCE(SUM(CASE WHEN d.isopioid = 'True' THEN qty ELSE 0 END), 0)):: numeric)/
				((COALESCE(SUM(qty), 0)):: numeric) * 100), 2):: float AS OpioidPortionOfPrescriptions
			FROM pd_triple t JOIN pd_drugs d ON t.drugname = d.drugname
				JOIN pd_prescriber p ON p.npi = t.prescriberid
			GROUP BY CONCAT(p.lname, ', ', p.fname)) t1
	WHERE t1.OpioidPortionOfPrescriptions > 0
	ORDER BY t1.OpioidPortionOfPrescriptions DESC) as t2
where t2.OpioidPortionOfPrescriptions = '100%';
    '''

    with connection.cursor() as cursor:
        cursor.execute(hundred)
        row = cursor.fetchall()
    results = {
        'count': len(row),
        'names': row[:10],
    }

    return results


# What opioid drug has been prescribed the most?
def query2():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT drugname AS Drug, SUM(qty) AS TotalPrescriptions FROM pd_triple GROUP BY drugname ORDER BY 2 DESC;")
        row = cursor.fetchall()
    max = row[0][1]
    q2 = []
    for i in range(0, len(row)):
        if row[i][1] < max:
            i = len(row)
        elif row[i][1] == max:
            q2.append(row[i])
    return q2

# Which state has the highest percentage of opioid related deaths compared to total population?


def query3():
    with connection.cursor() as cursor:
        cursor.execute('''
        select state, round(((deaths/population:: numeric)*100), 2) as DeathsPercentage
        from pd_statedata
		where deaths is not null
		and population is not null
        group by state, deaths, population
        order by (deaths/population:: float) desc''')
        row = cursor.fetchall()
    max = row[0][1]
    results = []
    for i in range(0, len(row)):
        if row[i][1] < max:
            i = len(row)
        elif row[i][1] == max:
            results.append(row[i])
    return results
