### ois-incidents
________________

This is project to scrape and re-serve officer involved shooting (OIS) incidents.  The first data set that is scraped comes from the [Deadspin project](http://regressing.deadspin.com/were-compiling-every-police-involved-shooting-in-americ-1624180387) which crowdsources OIS incident -- which is a fantastic project.  Currently, this project merely enhances the data by offering standardized documents served out as a REST API.  Consider, for example, the following query that searches for all incidents that involved Airsoft guns between 2011-2013:

**Example call:**
```bash
ois-incidents.appspot.com/content?limit=10&query=airsoft
```

```jsoniq
{
  count: 6,
  results: [
    {
      incident_date: null,
      city: "Santa Rosa",
      searched_date: "2013-10-22",
      victim_age: 13,
      shots_fired: 8,
      weapon: "airsoft replica of ak 47",
      victim_race: "hispanic or latino",
      agency: "Sonoma County Sheriffs Deputy",
      county: "Sonoma",
      source_url: "http://en.wikipedia.org/wiki/Shooting_of_Andy_Lopez",
      victim_armed: "unarmed",
      victim_name: "Andy Lopez",
      state: "CA",
      shootings: null,
      victim_gender: "male",
      outcome: "killed",
      summary: "The Deputy's encounter with Andy Lopez occurred in an open field. The boy's Airsoft replica AK 47 and a replica pistol looked realistic because not marked with orange tip.",
      officer_names: "Eric Gelhaus"
    },
    ...
  ]
}
```

The next step is to include the official OIS incidents from [Dallas](http://dallaspolice.net/ois/ois.html), [Philadelphia](http://www.phillypolice.com/ois), and San Francisco.  There are also unofficial records (like those from the Deadspin project) from (Oakland)[http://www.antievictionmappingproject.net/opd.html] or the [Fatal Encounters](http://www.fatalencounters.org/people-search/) database.  The objective is only to compile information from wherever possible, hopefully from official sources.

### Development

You'll need the database credentials in order to persistently store the OIS documents.  Please contact [**@danhammer**](http://www.github.com/danhammer) for the credentials.  Adding a source doesn't require access to these credentials, though.  Any help processing the OIS incidents into a standard form is much appreciated!
