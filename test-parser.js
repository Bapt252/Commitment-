function extractJobTitle(text) {
    const match = text.match(/intitulé\s+du\s+poste\s*:\s*([^\n\r]+)/i);
    if (match) {
        let title = match[1].trim();
        title = title.replace(/\([hf\/\s]*\)/gi, '').trim();
        return title;
    }
    return 'Titre non détecté';
}

const test = "Intitulé du poste : Assistant(e) juridique";
console.log('🎯 Résultat:', extractJobTitle(test));
