// Sinhala crop name translations.
// NOTE: verify with a native speaker / agriculture officer before
// deploying to real farmers.
export const CROP_SINHALA = {
  Banana: "කෙසෙල්",
  Papaya: "පැපොල්",
  Mango: "අඹ",
  Pineapple: "අන්නාසි",
  Guava: "පේර",
  Jackfruit: "කොස්",
  Breadfruit: "දෙල්",
  Avocado: "අලිගැට පේර",
  Orange: "දොඩම්",
  Pomegranate: "දෙළුම්",
  Rambutan: "රඹුටන්",
  "Wood Apple": "දිවුල්",
  "Beli Fruit": "බෙලි",
  Soursop: "කටු අනෝදා",
  Mangosteen: "මැංගුස්ටින්",
  "Rose Apple": "ජම්බු",
  Gooseberry: "නෙල්ලි",
  Carrot: "කැරට්",
  Cabbage: "ගෝවා",
  Potato: "අර්තාපල්",
  Onion: "ලූනු",
  Pumpkin: "වට්ටක්කා",
  Brinjal: "වම්බටු",
  "Long Purple Eggplant": "වම්බටු",
  Manioc: "මඤ්ඤොක්කා",
  Taro: "කිරි අල",
  Drumsticks: "මුරුංගා",
  "Red Spinach": "නිවිති",
  "Winged Bean": "දඹල",
  "Bitter Melon": "කරවිල",
  "Asiatic Pennywort": "ගොටුකොළ",
  Pennywort: "ගොටුකොළ",
  Beetroot: "බීට්රූට්",
  "Custard Apple": "වැලි අනෝදා",
  "Knol-Khol": "නෝ කෝල්",
  Leeks: "ලීක්ස්",
  "Passion Fruit": "පැෂන් ෆෘට්",
};

export function getCropName(cropEn, lang) {
  if (lang === "si") return CROP_SINHALA[cropEn] || cropEn;
  return cropEn;
}

// The 14 Great Soil Groups of Sri Lanka (de Alwis & Panabokke, 1972
// classification), as used in crops.json's soilTypes.
export const SOIL_SINHALA = {
  "Reddish Brown Earths": "රතු දුඹුරු පස",
  "Red-Yellow Podzolic Soils": "රතු-කහ පොඩ්සොලික් පස",
  "Reddish Brown Latosolic Soils": "රතු දුඹුරු ලැටසොලික් පස",
  "Red-Yellow Latosols": "රතු-කහ ලැටසෝල් පස",
  "Non-Calcic Brown Soils": "කැල්සියම් රහිත දුඹුරු පස (කැල්සික් නොවන දුඹුරු පස)",
  "Immature Brown Loams": "නොමේරූ දුඹුරු ලෝම පස",
  "Alluvial Soils": "ඇලුවියල් පස (ජලවහ පස / සර්වභූමි පස)",
  "Low Humic Gley Soils": "පහත් හියුමික් ග්ලේ පස",
  Regosols: "රෙගොසෝල් පස",
  Grumusols: "ගෲමුසෝල් පස (කළු මැටි පස / කළු කපු පස)",
  "Bog and Half-Bog Soils": "බෝග් සහ අර්ධ බෝග් පස (බෝග් සහ හාෆ්-බෝග් පස)",
  Rendzinas: "රෙන්ඩ්සිනා පස",
  "Soils of the Old Alluvium": "පුරාණ ඇලුවියල් පස (පැරණි ජලවහ පස)",
  "Solodized Solonetz": "සොලොඩයිස්ඩ් සොලොනෙට්ස් පස (ලවණ සහිත පස)",
};

export function getSoilName(soilEn, lang) {
  if (lang === "si") return SOIL_SINHALA[soilEn] || soilEn;
  return soilEn;
}

// Static UI strings shown in both languages.
export const UI_STRINGS = {
  rainfallForecastTitle: {
    en: "Forecast rainfall for the next 12 months in",
    si: "ඉදිරි මාස 12ට අපේක්ෂිත වර්ෂාපතනය -",
  },
  longTermCropRecommendations: {
    en: "Long-term crop recommendations",
    si: "දිගු කාලීන බෝග නිර්දේශ",
  },
  recommendedProfitableCropsFor: {
    en: "Recommended profitable crops for",
    si: "නිර්දේශිත ලාභදායී බෝග",
  },
  districtLabel: {
    en: "District:",
    si: "දිස්ත්‍රික්කය :",
  },
  rankedByPredictedGain: {
    en: "Ranked by predicted price",
    si: "අනුමාන කරන මිල අනුව ශ්‍රේණිගත කර ඇත",
  },
};

export function t(key, lang) {
  return UI_STRINGS[key]?.[lang] ?? UI_STRINGS[key]?.en ?? key;
}
