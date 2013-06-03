amra-hr
=======

## chrono.txt

The time report tool chrono works on three textfiles:
<table>
    <tr>
        <th>Filename</th><th>Purpose</th>
    </tr>
    <tr>
        <td>&lt;year&gt;.conf</td>
        <td>The configuration file for a given year. Includes hollidays etc. Example name: <i>2013.conf</i></td>
    </tr>
    <tr>
        <td>user.conf</td>
        <td>The configuration file for the user. Includes name, id, employment percentage vacation etc.</td>
    </tr>
    <tr>
        <td>&lt;year&gt;-&lt;month&gt;.txt</td>
        <td>The report file for a given month. Example name: <i>2013-05.txt</i>
    </tr>
</table>

### year.conf
The file is for defining deviant days.
```
MARCH
28 -2 "Skärtorsdag"
29 "Långfredag"

APRIL
1 "Annandag påsk"
28 -2
30 -2 "Valborgsmässafton

MAY
1 "Första maj"
9 "Kristi himmelfärdsdag"
10 "Klämdag"

JUNE
6 "Nationaldagen"
21 "Midsommarafton"

DECEMBER
23 "Klämdag"
24 "Julafton"
25 "Juldagen"
26 "Annandag jul"
27 "Klämdag"
30 "Klämdag"
31 "Nyårsafton"
```
### user.conf
A file defining personal work settings.
```
Name: Jonatan Lindström
ID: 820303-xxxx
Employment: 100 %
Vacation: 30
Start: 2013-06-01
```

To enable changes in the personal configuration from a specific date you can redefine values after a date marker:
```
Name: Jonatan Lindström
ID: 820303-xxxx
Employment: 100 %
Vacation: 30
Start: 2013-06-01

[2013-08-01]
Employment: 50 %
```
### year-month.report
Format:
* One row per work day.
* Order: date, ([S | V] | [start_time end_time lunch_time [deviation]]) [comment]
* Date is one or two digits followed by period.
* Time is expressed in 24-hour format.
* Colon or period can seperate hours from minutes (8:00 or 8.00)
* Deviation starts with a minus ("-")
* Strings follow expected string behaviour including break characters.

Example:
```
3. 8:05 17:00 1:00
4. S "Hemma, feber"
5. 8:20 17:30 0:30 "Lunchmöte"
6. 8:00 17:19 1:00 -1:00 "Gjorde ärende på stan på eftermiddagen."
7. 7:30 16:30 0:50
8. V "Ledig fredag"
11. 9:00 17:00 1:00
```
