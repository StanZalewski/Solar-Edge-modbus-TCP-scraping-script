# Solar Edge Modbus TCP scraping script 
This repo contains code for scraping data from Solar Edge inverter using Modbus TCP protocol with saving the data to the Prometheus database using push_to_gateway.
The file run.py is used for opening the virtual python script and controling the basic setup, such as:
- Eneabling the display (to check if data pulled from inverter is correct)
- Enabling/disabling the use of additional Solar Edge meter that is connected via Modbus to the inverter as in configuration
### The scraper.py file scrapes the following information from inverter:
##### Data from inverter
- Status of inverter [40084]
- Inverter's lifetime production [40094]
- Current power production [40108]
- AC voltage on all three phases [40080], [40081], [40082]
##### Data from meter 
- Current power flow [40207]
- Power factor [40226]
- Total exported real energy [40227]
- Total imported real energy [40235]
#### To extend the scraping script the registers are available in a [Technical note from SolarEdge](https://knowledge-center.solaredge.com/sites/kc/files/sunspec-implementation-technical-note.pdf) starting from page 17.
## License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE.md) file for details.
