import urllib.request as req
import xml.etree.ElementTree as ET
import pandas as pd
import urllib.parse

def query_postcodes(postcodes, names):
    # Initialize empty lists to store data
    all_abns = []
    all_statuses = []
    all_names = []
    all_scores = []
    all_indicators = []
    all_states = []
    all_postcodes = []

    for postcode in postcodes:
        for name in names:
            # Ensure the name is URL-encoded
            encoded_name = urllib.parse.quote(name)

            # Search parameters and URL construction code
            legalName = ''
            tradingName = ''
            NSW = 'Y'
            SA = 'N'
            ACT = 'N'
            VIC = 'N'
            WA = 'N'
            NT = 'N'
            QLD = 'N'
            TAS = 'N'
            authenticationGuid = 'b03c103e-ab73-441a-946c-bfa45c609d63'

            # Construct the URL by inserting the search parameters specified above
            conn = req.urlopen('https://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/' +
                               'ABRSearchByNameSimpleProtocol?name=' + encoded_name +
                               '&postcode=' + postcode + '&legalName=' + legalName +
                               '&tradingName=' + tradingName + '&NSW=' + NSW +
                               '&SA=' + SA + '&ACT=' + ACT + '&VIC=' + VIC +
                               '&WA=' + WA + '&NT=' + NT + '&QLD=' + QLD +
                               '&TAS=' + TAS + '&authenticationGuid=' + authenticationGuid)

            # XML is returned by the webservice
            returnedXML = conn.read()
            root = ET.fromstring(returnedXML)

            # Define namespaces
            ns = {'abr': 'http://abr.business.gov.au/ABRXMLSearchRPC/literalTypes'}

            # Extract data from XML
            for record in root.findall('.//abr:searchResultsRecord', ns):
                abn_element = record.find('./abr:ABN/abr:identifierValue', ns)
                abn = abn_element.text if abn_element is not None else ''

                status_element = record.find('./abr:ABN/abr:identifierStatus', ns)
                status = status_element.text if status_element is not None else ''

                # Check for organization name in different places
                name_elements = [
                    record.find('./abr:mainName/abr:organisationName', ns),
                    record.find('./abr:mainTradingName/abr:organisationName', ns),
                    record.find('./abr:businessName/abr:organisationName', ns),
                    record.find('./abr:otherTradingName/abr:organisationName', ns)  # Include otherTradingName
                ]
                name = next((elem.text for elem in name_elements if elem is not None), '')

                # Check for score in different places
                score_elements = [
                    record.find('./abr:mainName/abr:score', ns),
                    record.find('./abr:mainTradingName/abr:score', ns),
                    record.find('./abr:businessName/abr:score', ns),
                    record.find('./abr:otherTradingName/abr:score', ns)  # Include otherTradingName
                ]
                score = int(next((elem.text for elem in score_elements if elem is not None), 0))

                # Check for isCurrentIndicator in different places
                indicator_elements = [
                    record.find('./abr:mainName/abr:isCurrentIndicator', ns),
                    record.find('./abr:mainTradingName/abr:isCurrentIndicator', ns),
                    record.find('./abr:businessName/abr:isCurrentIndicator', ns),
                    record.find('./abr:otherTradingName/abr:isCurrentIndicator', ns)  # Include otherTradingName
                ]
                indicator = next((elem.text for elem in indicator_elements if elem is not None), '')

                state_element = record.find('./abr:mainBusinessPhysicalAddress/abr:stateCode', ns)
                state = state_element.text if state_element is not None else ''

                postcode_element = record.find('./abr:mainBusinessPhysicalAddress/abr:postcode', ns)
                postcode = postcode_element.text if postcode_element is not None else ''

                # Append data to lists
                all_abns.append(abn)
                all_statuses.append(status)
                all_names.append(name)
                all_scores.append(score)
                all_indicators.append(indicator)
                all_states.append(state)
                all_postcodes.append(postcode)

    # Create a DataFrame
    data = {
        'ABN': all_abns,
        'Identifier Status': all_statuses,
        'Organisation Name': all_names,
        'Score': all_scores,
        'Is Current Indicator': all_indicators,
        'State Code': all_states,
        'Postcode': all_postcodes
    }
    df = pd.DataFrame(data)

    # Filter the DataFrame for accurate results
    filtered_df = df[(df['Score'] > 90) & (df['Identifier Status'] == 'Active')]

    # Remove duplicates based on 'Organisation Name'
    filtered_df = filtered_df.drop_duplicates(subset=['Organisation Name'], keep='first')

    # Save DataFrame to an Excel file
    filtered_df.to_excel('abn_data.xlsx', index=False)

    return filtered_df