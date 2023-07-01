CREATE OR REPLACE FUNCTION public.list_vacancies(
    p_keyword VARCHAR DEFAULT NULL,
    p_region VARCHAR DEFAULT NULL,
	p_page INTEGER DEFAULT 1,
	p_per_page INTEGER DEFAULT 10
)
RETURNS SETOF vacancies LANGUAGE plpgsql AS $function$
DECLARE
    s_keyword VARCHAR := CONCAT('%', p_keyword, '%');
    offset_val INTEGER := (p_page - 1) * p_per_page;
    area_val VARCHAR := CONCAT('%', p_region, '%');
BEGIN
    RETURN QUERY
    SELECT v.* FROM vacancies AS v
    WHERE
        (v.name LIKE s_keyword OR v.requirement LIKE s_keyword OR v.responsibility LIKE s_keyword)
        AND
        (v.area = COALESCE(p_region, v.area) OR v.area LIKE area_val OR address_city LIKE area_val)
    ORDER BY v.published_at DESC
    OFFSET offset_val LIMIT p_per_page;
END;
$function$;

-- select * from list_vacancies('python', 'Москва');
-- select * from list_vacancies(p_keyword => 'python', p_region => 'Москва', p_page => 2, p_per_page => 20);

код postgres:
