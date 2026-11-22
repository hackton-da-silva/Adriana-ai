const equipment = /\b(rolament\w*|mancal|mancais|laminad\w*|ltq|anel externo|anel interno|an[eé]is|vu001|bc4\w*)\b/i;
const technicalIntent = /\b(esquent\w*|quente|temperatura\w*|aquec\w*|ru[ií]d\w*|barulh\w*|vibra\w*|desgast\w*|lubrific\w*|graxa|[oó]leo|monta\w*|desmonta\w*|inspe\w*|falh\w*|manuten\w*|verific\w*|sintom\w*|problema\w*|folga\w*|sufixo|trinc\w*|parada)\b/i;

export function hasMaintenanceEquipment(text: string) {
  return equipment.test(text);
}

export function isMaintenanceTurn(query: string, recentTopic = '') {
  if (/\b(circul[ea]|circund\w*|desenh[ea]|mostre na tela)\b/i.test(query)) return false;
  return technicalIntent.test(query) && (hasMaintenanceEquipment(query) || hasMaintenanceEquipment(recentTopic));
}

export function maintenanceSearchTerms(query: string) {
  const concepts: [RegExp, string][] = [
    [/inspe\w*|verific\w*|parada/i, 'bearing inspection periodically operating'],
    [/ru[ií]d\w*|barulh\w*/i, 'unusual noises'],
    [/esquent\w*|quente|temperatura\w*|aquec\w*/i, 'high running temperatures'],
    [/vibra\w*/i, 'bearing vibration'],
    [/desgast\w*|trinc\w*|falh\w*/i, 'wear damage failure'],
    [/lubrific\w*|graxa|[oó]leo/i, 'lubrication grease oil'],
    [/monta\w*|desmonta\w*/i, 'assembly mounting dismounting'],
    [/folga\w*/i, 'internal clearance'],
    [/registro\w*|hist[oó]ric\w*/i, 'maintenance record keeping'],
    [/anel externo/i, 'outer ring'],
    [/anel interno/i, 'inner ring'],
  ];
  return [query.match(/\b(?:VU001|BC4\w*(?:-\d+)?)\b/gi)?.join(' '),
    ...concepts.filter(([pattern]) => pattern.test(query)).map(([, term]) => term)]
    .filter(Boolean).join(' ');
}
