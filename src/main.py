import requests
import pandas as pd
from bs4 import BeautifulSoup

class GNULicense:
    def __init__(
        self,
        url: str,
        ids: set,
        title: str,
        description: str,
    ) -> None:
        self.url = url
        self.ids = ids
        self.title = title
        self.description = description

class GNULicenseGroup:
    def __init__(
        self,
        name: str,
        selector: str,
        description: str,
    ) -> None:
        self.name = name
        self.selector = selector
        self.description = description
        self.licenses: list[GNULicense] = []

class GNULicenseScraper:
    def __init__(self) -> None:
        self.groups: list[GNULicenseGroup] = [
            GNULicenseGroup(
                name='gnu',
                selector='dl.green:nth-child(5)',
                description='Free licenses, compatible with the GNU GPL',
            ),
            GNULicenseGroup(
                name='free',
                selector='dl.orange:nth-child(9)',
                description='Free licenses, incompatible with the GNU GPL and FDL',
            ),
            GNULicenseGroup(
                name='nonfree',
                selector='dl.red:nth-child(16)',
                description='Nonfree licenses',
            ),
        ]

    def scrap(self) -> None:
        url = 'https://www.gnu.org/licenses/license-list.html'
        response = requests.get(url=url)
        soup = BeautifulSoup(
            markup=response.text,
            features='html.parser',
        )

        for group in self.groups:
            group_soup = soup.select_one(group.selector)

            for license_soup_dt in group_soup.select('dt'):
                if license_soup_dt.get('id') != None:
                    if license_soup_dt.get('id') == 'Wx':
                        group.licenses.append(GNULicense(
                            url='https://directory.fsf.org/wiki/License:WxWindows_Library_Licence-3.1',
                            ids=['Wx'],
                            title='WxWidgets Library License',
                            description='',
                        ))
                        continue

                    if license_soup_dt.get('id') == 'Wxwind':
                        group.licenses.append(GNULicense(
                            url='https://directory.fsf.org/wiki/License:WxWindows_Library_Licence-3.1',
                            ids=['Wxwind'],
                            title='WxWindows Library License',
                            description='An old name for the WxWidgets Library License',
                        ))
                        continue

                license_as = license_soup_dt.select('a')

                license_ids = set()
                license_url = ''
                license_title = ''
                for license_a in license_as:
                    if license_a.get('id') == None:
                        continue

                    license_ids.add(license_a.get('id').strip())
                    license_url = (license_a.get('href') or '') if len(license_url) == 0 else license_url
                    license_title = (license_a.text or '') if len(license_title) == 0 else license_title

                license_soup_dd = license_soup_dt.find_next_sibling('dd')

                license_description = ''
                license_ps = license_soup_dd.select('p')
                for license_p in license_ps:
                    license_description += license_p.text.strip() + '\n'

                license_url = f'https:{license_url}' if license_url.startswith('//') else license_url
                license_url = f'https://www.gnu.org{license_url}' if not license_url.startswith('http') else license_url
                license = GNULicense(
                    url=license_url.strip(),
                    ids=license_ids,
                    title=license_title.strip() if len(license_title) > 0 else license_soup_dt.text.strip(),
                    description=license_description,
                )

                group.licenses.append(license)

    def to_list(self) -> list[dict]:
        data = []
        for group in self.groups:
            for license in group.licenses:
                data.append({
                    'ids': ','.join(license.ids),
                    'title': license.title.replace('\n', ' '),
                    # 'description': license.description,
                    'url': license.url,
                    'summary': group.description,
                    'is_gnu_compatible': group.name == 'gnu',
                    'is_free': group.name == 'free' or group.name == 'gnu',
                })

        return data

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.to_list())

def main():
    scraper = GNULicenseScraper()
    scraper.scrap()

    df = scraper.to_dataframe()
    df.to_csv('data/licenses.csv', index=False)
    df.to_json('data/licenses.json', orient='records')
    df.to_html('data/licenses.html', index=False)
    df.to_excel('data/licenses.xlsx', index=False)
    df.to_latex('data/licenses.tex', index=False)
    df.to_markdown('data/licenses.md', index=False)

if __name__ == '__main__':
    main()
