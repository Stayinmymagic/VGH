# 整理空氣檢測站資料

#### 目的
* 將77個空氣檢測站的數值經由空污指數公式轉換成空污指標
* 根據經緯度位置以及線性插值法，從77個空氣檢測站資料推算出349個鄉鎮市區的空污指標表現
* 根據病人看診日期往回推一年，病人所居住位置的空污指標表現，提供給醫師進一步研究

#### 檔案說明
* zip_fit_station.py : 從郵政代碼區域的經緯度位置配對五個鄰近的空氣檢測站
* xls_trans_to_pk.py : 將空氣檢測站資料依照地區、時間、空氣檢測數值整理成巢狀字典並存成pickle
* patient_3y_record.py : 根據病人居住位置利用線性插值估算空氣檢測數值，並根據就診日期往回推三年（回推年數可更改），計算三年內空氣指標表現（如六項空氣指數的AQI指標最大值、最小值、平均、在各區間的天數統計等基礎統計資料）
* patient_3y_record_psi.py : 空污指標公式改為PSI
* record_for_township_new.py : 醫師希望能取得在疫情前及疫情間各鄉鎮市區空氣指標統計資料，因此資料區間設定自2019/01/01至2021/06/30，計算各鄉鎮市區在這兩年半間的空氣指標表現。（輸出資料的欄位與patient_3y_record.py相同）
* record_for_township_new_psi.py : 空污指標公式改為PSI


#### 資料來源
* 全台灣77個空氣檢測站歷年資料
* https://airtw.epa.gov.tw/CHT/Query/His_Data.aspx
* 僅放上程式碼，並無提供病人資料

#### 輸出資料參考
* record_for_township_new.py 輸出各鄉鎮市區空氣指標表現：
* https://drive.google.com/drive/folders/1DbR7UmrGLqy8MfChwMZaxprSfZv-XCKf?usp=sharing
