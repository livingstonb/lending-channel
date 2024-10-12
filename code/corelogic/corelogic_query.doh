


#delimit ;

/* Create local for tax table name */
if  (`yy'`mmdd1' < 20150401) {;
	/* Fix property characteristics for all pre-2015q2 transactions */
	local tax_table tax_2015_q2;
};
else {;
	local tax_table tax_`yy'_q`qq';
};


/* Query */
cap odbc load,
		dsn("SimbaAthena")
		exec(`"
		SELECT
			d."fips code",
			d."apn unformatted",
			d."apn sequence number",
			d."recording date",
			d."sale date",
			d."sale amount",
			d."resale new construction code",
			d."batch id",
			d."batch seq"
			t."year`_s_'built",
			t."land`_s_'square`_s_'footage",
			t."universal`_s_'building`_s_'square`_s_'feet",
			t."property`_s_'zipcode",
			t."bedrooms",
			t."total`_s_'baths",
			t."total`_s_'baths`_s_'calculated",
			t."construction`_s_'type`_s_'code",
			t."exterior`_s_'walls`_s_'code",
			t."fireplace`_s_'number",
			t."parking`_s_'spaces",
			t."pool`_s_'flag",
			t."quality`_s_'code",
			t."stories`_s_'number",
			t."units`_s_'number",
			t."view"
		FROM
			corelogic.deed as d
		INNER JOIN corelogic.`tax_table' as t
			ON (t."FIPS`_s_'CODE"=d."FIPS CODE")
				AND (t."APN`_s_'UNFORMATTED"=d."APN UNFORMATTED")
				AND (cast(t."APN`_s_'SEQUENCE`_s_'NUMBER" as bigint)
							=d."APN SEQUENCE NUMBER")
		WHERE (d."pri cat code" IN ('A'))
			AND (d."${datevar} date" BETWEEN `yy'`mmdd1' AND `yy'`mmdd2')
			AND (d."mortgage sequence number" is NULL)
			AND (d."property indicator code" in ('10'))
			AND (d."sale amount" > 0)
		ORDER BY
			d."sale date",
			d."fips code",
			d."apn unformatted",
			d."apn sequence number"
	"');
