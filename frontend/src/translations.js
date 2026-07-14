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
};

export function getCropName(cropEn, lang) {
  if (lang === "si") return CROP_SINHALA[cropEn] || cropEn;
  return cropEn;
}
