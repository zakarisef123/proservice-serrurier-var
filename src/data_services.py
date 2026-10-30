# -*- coding: utf-8 -*-
"""Prestations de serrurerie. Chaque service génère une page dédiée et une page par commune."""

SERVICES = [
    # ------------------------------------------------------------------ URGENCE
    {
        "slug": "serrurier-urgence-24h-var",
        "image": "serrurier-urgence.jpg",
        "image_alt": "Serrurier en intervention d'urgence devant une porte d'entrée",
        "combo": "serrurier-urgence",
        "name": "Serrurier urgence 24h/24",
        "short": "Urgence serrurerie 24h/24",
        "icon": "bolt",
        "badge": "Urgence 24/7",
        "price_label": "Tarif annoncé avant déplacement",
        "price_min": None,
        "title": "Serrurier urgence 24h/24 dans le Var — nuit, week-end, jours fériés",
        "meta": "Serrurier d'urgence dans le Var 24h/24 et 7j/7 : porte claquée, clés perdues, serrure bloquée, effraction. Tarif annoncé avant déplacement. ☎ 06 75 93 19 04",
        "h1": "Serrurier d'urgence 24h/24 et 7j/7 dans le Var",
        "lead": "Porte claquée, clés perdues, serrure bloquée, porte forcée : un serrurier vous répond <b>jour et nuit, week-end et jours fériés compris</b>, depuis Vidauban vers tout le centre Var.",
        "checks": ["Réponse immédiate au téléphone", "Prix annoncé avant de partir", "Facture pour l'assurance"],
        "card_desc": "Porte claquée, clés perdues, effraction : un serrurier joignable jour et nuit, week-end et jours fériés compris.",
        "card_checks": ["Disponible 7j/7", "Tarif confirmé avant déplacement"],
        "sections": [
            ("Quelles situations justifient un serrurier en urgence ?",
             "<p>Certaines situations ne peuvent pas attendre le lendemain. Nous intervenons en priorité pour :</p>"
             "<ul><li><strong>Une porte claquée</strong> : vous êtes dehors, les clés sont à l'intérieur.</li>"
             "<li><strong>Des clés perdues ou volées</strong> : impossible de rentrer, et risque que quelqu'un d'autre puisse le faire.</li>"
             "<li><strong>Une clé cassée dans la serrure</strong> ou une serrure qui ne tourne plus.</li>"
             "<li><strong>Une porte forcée après un cambriolage</strong> : il faut sécuriser le logement le soir même.</li>"
             "<li><strong>Un rideau métallique bloqué</strong> : commerce impossible à ouvrir ou à fermer.</li></ul>"
             "<p>Au téléphone, nous vous aidons à évaluer la situation. Si l'intervention peut attendre le lendemain sans risque, nous vous le disons : un déplacement de nuit coûte plus cher et nous préférons vous éviter cette dépense lorsqu'elle n'est pas nécessaire.</p>"),
            ("Les bons réflexes en attendant le serrurier",
             "<ol><li><strong>Vérifiez les autres accès</strong> : porte de garage, porte-fenêtre, un voisin ou un proche qui aurait un double.</li>"
             "<li><strong>N'essayez pas de forcer</strong> la serrure vous-même : vous risquez d'abîmer la porte et d'alourdir la facture.</li>"
             "<li><strong>Préparez un justificatif</strong> : pièce d'identité ou justificatif de domicile, demandé sur place pour toute ouverture.</li>"
             "<li><strong>En cas d'effraction</strong>, ne touchez à rien, appelez la police (17) et prenez des photos pour l'assurance.</li></ol>"
             "<p>Vous hésitez sur la démarche ? Appelez-nous : nous vous guidons au téléphone pendant que le serrurier est en route.</p>"),
            ("Serrurier la nuit, le dimanche et les jours fériés",
             "<p>Une porte claquée ne prévient pas. La ligne <strong>06 75 93 19 04</strong> est joignable 24h/24, y compris le dimanche, les jours fériés et pendant les vacances. Les interventions de nuit, de week-end ou de jour férié peuvent faire l'objet d'un supplément horaire : <strong>il vous est toujours communiqué avant le déplacement</strong>, jamais découvert sur la facture.</p>"
             "<p>Ce fonctionnement transparent est l'inverse des pratiques régulièrement dénoncées dans le dépannage de serrurerie. Vous savez ce que vous allez payer avant que le serrurier ne prenne la route, et le prix est confirmé sur place avant tout travail.</p>"),
            ("Une intervention propre et sans casse quand c'est possible",
             "<p>Dans la grande majorité des cas, une porte claquée s'ouvre sans dégât, avec des outils adaptés. Si la serrure doit être percée ou remplacée, c'est toujours <strong>annoncé et validé avec vous avant</strong>. À la fin, vous recevez une facture détaillée, utile si votre assurance prend en charge l'intervention.</p>"),
        ],
        "faq": [
            ("Combien coûte un serrurier en urgence la nuit ou le dimanche ?", "Le prix dépend de la situation et de l'horaire. Un supplément peut s'appliquer la nuit, le week-end et les jours fériés : il vous est annoncé au téléphone avant le déplacement, puis le prix total est confirmé sur place avant de commencer."),
            ("En combien de temps un serrurier peut-il arriver ?", "Depuis notre base de Vidauban, comptez environ 15 minutes pour Le Muy, Les Arcs ou Le Cannet-des-Maures, 20 minutes pour Le Luc et 25 minutes pour Draguignan, hors trafic. Le délai précis vous est donné au moment de l'appel."),
            ("Faut-il justifier son identité pour une ouverture de porte ?", "Oui. Une pièce d'identité ou un justificatif de domicile est demandé sur place, pour la sécurité de l'occupant réel du logement."),
            ("Intervenez-vous après un cambriolage ?", "Oui. Nous sécurisons le logement le jour même (remplacement de serrure ou fermeture provisoire) et vous remettons une facture détaillée pour votre déclaration à l'assurance."),
        ],
        "combo_h1": "Serrurier d'urgence 24h/24",
        "combo_title": "Serrurier urgence {city} ({cp}) — 24h/24, 7j/7",
        "combo_meta": "Serrurier d'urgence {a} 24h/24 et 7j/7 : porte claquée, clés perdues, serrure bloquée, effraction. {delay_txt}. Prix annoncé avant déplacement. ☎ 06 75 93 19 04",
        "combo_intros": [
            "Porte claquée un soir de week-end, clés perdues, serrure bloquée : {a}, vous pouvez joindre un serrurier à toute heure au <b>06 75 93 19 04</b>. Nous partons de Vidauban et le délai d'arrivée vous est donné dès l'appel.",
            "Besoin d'un serrurier tout de suite {a} ? Notre ligne est ouverte jour et nuit, dimanches et jours fériés compris. Vous décrivez la situation, on vous annonce le prix et le délai, puis un serrurier part avec le matériel adapté.",
            "Habitants {de}, gardez ce numéro : <b>06 75 93 19 04</b>. En cas d'urgence de serrurerie, un artisan du secteur vous répond directement, sans plateforme ni centre d'appel, et intervient rapidement avec un prix annoncé à l'avance.",
        ],
        "combo_points": [
            "Porte claquée, clés à l'intérieur",
            "Clés perdues ou volées",
            "Clé cassée dans la serrure",
            "Serrure bloquée ou grippée",
            "Porte forcée après un cambriolage",
            "Rideau métallique bloqué",
        ],
        "combo_tip": "En attendant notre arrivée, vérifiez les autres accès et préparez une pièce d'identité ou un justificatif de domicile : il vous sera demandé avant toute ouverture de porte.",
    },
    # ------------------------------------------------------------------ OUVERTURE
    {
        "slug": "ouverture-de-porte-var",
        "image": "ouverture-de-porte.jpg",
        "image_alt": "Ouverture d'une porte d'entrée par un serrurier",
        "combo": "ouverture-porte",
        "name": "Ouverture de porte",
        "short": "Ouverture de porte",
        "icon": "key",
        "badge": "Urgence 24/7",
        "price_label": "à partir de 69 €",
        "price_min": 69,
        "title": "Ouverture de porte dans le Var — porte claquée ou fermée, dès 69 €",
        "meta": "Ouverture de porte claquée ou fermée à clé dans le Var, 24h/24 : sans casse dans la majorité des cas, dès 69 €. Prix annoncé avant intervention. ☎ 06 75 93 19 04",
        "h1": "Ouverture de porte claquée ou fermée à clé dans le Var",
        "lead": "Porte claquée, clés perdues ou cassées, serrure bloquée : nous ouvrons votre porte <b>sans dégâts dans la majorité des cas</b>, 24h/24. Intervention à partir de 69 €.",
        "checks": ["Ouverture sans casse quand c'est possible", "Prix annoncé avant de commencer", "Disponible 24h/24"],
        "card_desc": "Porte claquée, clé cassée ou perdue ? Nous ouvrons votre porte sans dégâts dans la majorité des cas.",
        "card_checks": ["Sans casse", "Technique de poussée"],
        "sections": [
            ("Porte claquée ou porte fermée à clé : ce n'est pas la même chose",
             "<p>Le prix et la technique d'ouverture dépendent d'abord de l'état de votre porte :</p>"
             "<ul><li><strong>Porte claquée</strong> : seul le pêne demi-tour (celui qui se ferme quand on tire la porte) retient la porte. Elle s'ouvre le plus souvent <strong>sans aucun dégât</strong>, avec des outils spécifiques glissés entre la porte et le dormant.</li>"
             "<li><strong>Porte fermée à clé</strong> : les pênes dormants sont engagés. Selon la serrure, l'ouverture se fait par crochetage ou, pour les serrures haute sécurité, par perçage du cylindre, qui doit alors être remplacé.</li>"
             "<li><strong>Clé cassée ou bloquée</strong> : nous extrayons le morceau de clé, puis nous vérifions le cylindre.</li></ul>"
             "<p>Au téléphone, décrivez votre porte (porte claquée ou fermée à clé, type de serrure, porte blindée ou non) : nous vous donnons une fourchette de prix avant de partir.</p>"),
            ("Nos méthodes d'ouverture",
             "<ul><li><strong>Ouverture fine (technique de poussée)</strong> pour les portes claquées : aucune trace, la serrure reste intacte.</li>"
             "<li><strong>Crochetage</strong> des cylindres qui s'y prêtent.</li>"
             "<li><strong>Extraction de clé cassée</strong> avec des outils dédiés.</li>"
             "<li><strong>Perçage du cylindre</strong> en dernier recours, uniquement avec votre accord : le cylindre est alors remplacé sur place.</li></ul>"
             "<div class=\"callout\"><strong>Sécurité :</strong> une pièce d'identité ou un justificatif de domicile vous est demandé avant toute ouverture. C'est une garantie pour vous : personne ne peut faire ouvrir votre logement à votre place.</div>"),
            ("Après l'ouverture",
             "<p>Si vos clés ont été perdues ou volées, nous vous conseillons de <strong>changer le cylindre</strong> : quelqu'un pourrait les utiliser. Nous pouvons le faire dans la foulée, avec un cylindre adapté à votre porte et à votre budget. <a href=\"/changement-serrure-var/\">Voir le changement de serrure</a>.</p>"),
        ],
        "faq": [
            ("Combien coûte une ouverture de porte ?", "Le tarif de base démarre à 69 € en journée. Il dépend du type de serrure et de l'horaire ; il est toujours confirmé avant intervention, jamais après."),
            ("La porte sera-t-elle abîmée ?", "Dans la majorité des cas, non : une porte claquée s'ouvre sans dégât. Si la serrure doit être forcée ou percée, c'est toujours annoncé et validé avant."),
            ("Pouvez-vous ouvrir une porte blindée ?", "Oui. L'ouverture d'une porte blindée fermée à clé demande souvent le perçage du cylindre, remplacé ensuite sur place. Le prix vous est annoncé avant."),
            ("Faut-il être propriétaire pour faire ouvrir une porte ?", "Non, mais vous devez justifier que vous occupez le logement : pièce d'identité avec l'adresse, justificatif de domicile ou bail."),
        ],
        "combo_h1": "Ouverture de porte",
        "combo_title": "Ouverture de porte {city} ({cp}) — porte claquée dès 69 €",
        "combo_meta": "Ouverture de porte {a} 24h/24 : porte claquée ou fermée à clé, sans casse dans la majorité des cas, dès 69 €. {delay_txt}. ☎ 06 75 93 19 04",
        "combo_intros": [
            "Porte claquée ou clés perdues {a} ? Nous ouvrons votre porte 24h/24, sans dégât dans la majorité des cas, à partir de 69 €.",
            "Vous êtes bloqué dehors {a} ? Un serrurier part de Vidauban avec le matériel d'ouverture adapté. Le prix vous est annoncé au téléphone, avant le déplacement.",
            "Ouverture de porte claquée, fermée à clé ou porte blindée {a} : nous choisissons la technique la moins destructive et vous annonçons le prix avant de commencer.",
        ],
        "combo_points": [
            "Porte claquée, clés à l'intérieur",
            "Porte fermée à clé, clés perdues",
            "Clé cassée dans la serrure",
            "Ouverture de porte blindée",
            "Serrure bloquée ou grippée",
            "Ouverture de boîte aux lettres",
        ],
        "combo_tip": "Avant notre arrivée, préparez une pièce d'identité ou un justificatif de domicile (même sur votre téléphone) : il vous sera demandé avant l'ouverture.",
    },
    # ------------------------------------------------------------------ SERRURE
    {
        "slug": "changement-serrure-var",
        "image": "changement-serrure.jpg",
        "image_alt": "Serrurier remplaçant une serrure de porte d'entrée",
        "combo": "changement-serrure",
        "name": "Changement de serrure",
        "short": "Remplacement serrure",
        "icon": "lock",
        "badge": "Serrures A2P",
        "price_label": "à partir de 129 €",
        "price_min": 129,
        "title": "Changement de serrure dans le Var — serrures A2P, dès 129 €",
        "meta": "Changement de serrure et de cylindre dans le Var : serrures certifiées A2P, multipoints, à l'identique ou en montée en gamme. Garantie 2 ans, dès 129 €. ☎ 06 75 93 19 04",
        "h1": "Changement de serrure et de cylindre dans le Var",
        "lead": "Clés perdues, tentative d'effraction, serrure usée ou montée en gamme : nous installons des <b>serrures et cylindres certifiés A2P</b>, à l'identique ou plus sûrs. À partir de 129 €, garantie 2 ans.",
        "checks": ["Serrures certifiées A2P", "Garantie 2 ans", "Conseil sur le niveau de sécurité"],
        "card_desc": "Installation et remplacement de serrures haute sécurité certifiées A2P, à l'identique ou en montée en gamme.",
        "card_checks": ["Serrures certifiées", "Garantie 2 ans"],
        "sections": [
            ("Quand faut-il changer sa serrure ?",
             "<ul><li>après la <strong>perte ou le vol de vos clés</strong> ;</li>"
             "<li>après un <strong>cambriolage ou une tentative d'effraction</strong> ;</li>"
             "<li>lors d'un <strong>emménagement</strong> : vous ne savez pas qui possède encore un double ;</li>"
             "<li>quand la serrure est <strong>usée, grippée</strong> ou que la clé tourne difficilement ;</li>"
             "<li>pour <strong>monter en sécurité</strong>, ou parce que votre assurance exige une serrure certifiée.</li></ul>"
             "<p>Souvent, il suffit de remplacer le <strong>cylindre</strong> (la partie où l'on insère la clé) : c'est plus rapide et moins cher que de changer toute la serrure.</p>"),
            ("Comprendre la certification A2P",
             "<p>La certification <strong>A2P</strong>, délivrée par le CNPP, garantit qu'une serrure ou un cylindre résiste un temps minimum aux tentatives d'effraction :</p>"
             "<div class=\"table-scroll\"><table><thead><tr><th>Niveau</th><th>Résistance minimale à l'effraction</th></tr></thead><tbody>"
             "<tr><td>A2P ★</td><td>5 minutes</td></tr>"
             "<tr><td>A2P ★★</td><td>10 minutes</td></tr>"
             "<tr><td>A2P ★★★</td><td>15 minutes</td></tr></tbody></table></div>"
             "<p>De nombreux contrats d'assurance habitation imposent une serrure certifiée, parfois avec plusieurs points de fermeture. Vérifiez votre contrat : nous vous conseillons le niveau adapté à votre porte, à votre logement et à votre budget.</p>"),
            ("Serrures que nous posons",
             "<ul><li><strong>Cylindres</strong> européens standards, de sécurité et haute sécurité.</li>"
             "<li><strong>Serrures en applique</strong> et <strong>serrures à larder</strong> (encastrées).</li>"
             "<li><strong>Serrures multipoints</strong> (3 ou 5 points) pour renforcer une porte existante.</li>"
             "<li><strong>Verrous</strong> et <strong>serrures de garage</strong>, portails et boîtes aux lettres.</li></ul>"
             "<p>Nous travaillons avec les principales marques du marché et pouvons remplacer votre serrure à l'identique ou proposer une montée en gamme. Tous les remplacements sont garantis 2 ans.</p>"),
        ],
        "faq": [
            ("Combien coûte le changement d'une serrure ?", "À partir de 129 €. Le prix dépend du type de serrure (cylindre seul, applique, multipoints) et du niveau de sécurité choisi ; il est annoncé avant intervention."),
            ("Faut-il changer toute la serrure ou seulement le cylindre ?", "Après une perte de clés, changer le cylindre suffit souvent. Après une effraction, la serrure peut être endommagée : nous vérifions et vous conseillons."),
            ("Combien de temps dure un changement de serrure ?", "Un changement de cylindre prend généralement moins d'une heure. Une serrure multipoints demande plus de temps selon la porte."),
            ("Les serrures sont-elles garanties ?", "Oui, nos remplacements de serrure sont garantis 2 ans, pièces et main-d'œuvre."),
        ],
        "combo_h1": "Changement de serrure",
        "combo_title": "Changement de serrure {city} ({cp}) — A2P dès 129 €",
        "combo_meta": "Changement de serrure et de cylindre {a} : serrures A2P, multipoints, garantie 2 ans, dès 129 €. {delay_txt}. ☎ 06 75 93 19 04",
        "combo_intros": [
            "Clés perdues, effraction ou serrure usée {a} : nous remplaçons votre cylindre ou votre serrure par un modèle certifié A2P, à partir de 129 €, garantie 2 ans.",
            "Vous venez d'emménager {a} ou avez perdu vos clés ? Changer le cylindre est le moyen le plus sûr de reprendre le contrôle de vos accès. Nous intervenons rapidement depuis Vidauban.",
            "Changement de serrure {a} : à l'identique ou en montée en gamme, avec un conseil honnête sur le niveau de sécurité dont vous avez vraiment besoin.",
        ],
        "combo_points": [
            "Remplacement de cylindre",
            "Serrure multipoints 3 ou 5 points",
            "Serrure certifiée A2P",
            "Serrure après effraction",
            "Changement de serrure après emménagement",
            "Verrou et serrure de garage",
        ],
        "combo_tip": "Si vous avez perdu vos clés avec un papier portant votre adresse, faites changer le cylindre sans attendre : c'est la seule façon d'être sûr que personne ne pourra les utiliser.",
    },
    # ------------------------------------------------------------------ PORTE BLINDEE
    {
        "slug": "porte-blindee-var",
        "image": "porte-blindee.jpg",
        "image_alt": "Serrure multipoints haute sécurité sur une porte blindée",
        "combo": "porte-blindee",
        "name": "Porte blindée & blindage de porte",
        "short": "Porte blindée",
        "icon": "shield",
        "badge": "Sécurité max",
        "price_label": "sur devis",
        "price_min": None,
        "title": "Porte blindée dans le Var — pose, blindage de porte, serrure multipoints",
        "meta": "Pose de porte blindée et blindage de porte existante dans le Var : serrures multipoints certifiées A2P, bloc-porte certifié. Devis gratuit. ☎ 06 75 93 19 04",
        "h1": "Porte blindée et blindage de porte dans le Var",
        "lead": "Pose d'un <b>bloc-porte blindé</b> ou blindage de votre porte existante, serrure multipoints certifiée A2P : nous renforçons l'accès principal de votre logement, avec un devis gratuit et détaillé.",
        "checks": ["Devis gratuit et détaillé", "Serrures multipoints A2P", "Pose soignée"],
        "card_desc": "Installation de portes blindées et serrures multipoints pour une sécurité maximale de votre logement.",
        "card_checks": ["Certifié A2P", "Multipoints"],
        "sections": [
            ("Bloc-porte blindé ou blindage de porte ?",
             "<ul><li><strong>Le bloc-porte blindé</strong> remplace toute la porte et son cadre. C'est la solution la plus sûre : la porte, le cadre et la serrure sont conçus ensemble.</li>"
             "<li><strong>Le blindage de porte</strong> renforce votre porte existante : plaque d'acier, cornières anti-pince, serrure multipoints et protège-cylindre. Il coûte moins cher et convient quand la porte et le cadre sont en bon état.</li></ul>"
             "<p>Lors de la visite, nous examinons votre porte, votre cadre et votre mur pour vous conseiller la solution adaptée, sans surdimensionner.</p>"),
            ("Les certifications à connaître",
             "<p>Les blocs-portes peuvent être certifiés <strong>A2P BP1, BP2 ou BP3</strong>, selon leur résistance à l'effraction (respectivement 5, 10 et 15 minutes minimum). Les serrures et cylindres ont leur propre certification A2P de une à trois étoiles. Certains assureurs les exigent pour des contrats avec garanties vol élevées : vérifiez votre contrat avant de choisir.</p>"),
            ("Une pose soignée",
             "<p>Une porte blindée n'est efficace que si elle est bien posée : fixation dans un mur sain, réglage précis des points de fermeture, finitions intérieures et extérieures. Nous protégeons les sols, évacuons l'ancienne porte et réglons la porte jusqu'à ce qu'elle ferme parfaitement.</p>"),
        ],
        "faq": [
            ("Combien coûte une porte blindée ?", "Le prix dépend du type de bloc-porte, de la certification, des finitions et des travaux de pose. Après une visite gratuite, nous vous remettons un devis détaillé."),
            ("Peut-on blinder une porte existante ?", "Oui, si la porte et son cadre sont en bon état. Le blindage ajoute une plaque d'acier, des cornières et une serrure multipoints."),
            ("Combien de temps dure la pose ?", "Le blindage d'une porte existante se fait généralement dans la journée. La pose d'un bloc-porte dépend de la fabrication et des travaux de maçonnerie."),
            ("Une porte blindée est-elle exigée par les assurances ?", "Pas systématiquement, mais certains contrats l'imposent ou accordent de meilleures garanties avec une porte et une serrure certifiées. Vérifiez votre contrat."),
        ],
        "combo_h1": "Porte blindée et blindage de porte",
        "combo_title": "Porte blindée {city} ({cp}) — pose et blindage de porte",
        "combo_meta": "Porte blindée {a} : pose de bloc-porte, blindage de porte existante, serrure multipoints A2P. Visite et devis gratuits. {delay_txt}. ☎ 06 75 93 19 04",
        "combo_intros": [
            "Vous voulez renforcer la porte d'entrée de votre logement {a} ? Nous posons des blocs-portes blindés et blindons les portes existantes, avec serrure multipoints certifiée A2P.",
            "Pour une porte blindée {a}, nous commençons par une visite gratuite : état de la porte, du cadre et du mur, puis devis détaillé selon la solution adaptée.",
            "Bloc-porte blindé ou blindage de votre porte actuelle {a} : nous vous aidons à choisir la bonne solution, au juste prix, et assurons une pose soignée.",
        ],
        "combo_points": [
            "Pose de bloc-porte blindé",
            "Blindage de porte existante",
            "Serrure multipoints A2P",
            "Cornières anti-pince",
            "Protège-cylindre",
            "Réglage de porte blindée",
        ],
        "combo_tip": "Avant la visite, notez la référence de votre contrat d'assurance habitation : certains contrats exigent une porte ou une serrure certifiée, ce qui oriente le choix.",
    },
    # ------------------------------------------------------------------ CLES
    {
        "slug": "reproduction-cles-var",
        "image": "reproduction-cles.jpg",
        "image_alt": "Clé insérée dans un cylindre de serrure",
        "combo": "reproduction-cles",
        "name": "Reproduction de clés",
        "short": "Reproduction de clés",
        "icon": "key",
        "badge": "Sur place",
        "price_label": "à partir de 15 €",
        "price_min": 15,
        "title": "Reproduction de clés dans le Var — double de clé dès 15 €",
        "meta": "Reproduction de clés dans le Var : clés standards, clés sécurisées avec carte de propriété, clés à passe. Double de clé dès 15 €. ☎ 06 75 93 19 04",
        "h1": "Reproduction de clés dans le Var",
        "lead": "Double de clé standard, clé sécurisée avec carte de propriété, organigramme : nous reproduisons vos clés <b>sur place ou en atelier partenaire</b>. À partir de 15 €.",
        "checks": ["Tous types de clés", "Clés sécurisées avec carte", "Délai rapide"],
        "card_desc": "Copie de clés standards, sécurisées et à passe, réalisée sur place ou en atelier partenaire.",
        "card_checks": ["Livraison rapide", "Tous types de clés"],
        "sections": [
            ("Les clés que nous reproduisons",
             "<ul><li><strong>Clés standards</strong> de porte d'entrée, de garage, de boîte aux lettres.</li>"
             "<li><strong>Clés de sécurité et haute sécurité</strong>, protégées par une carte de propriété.</li>"
             "<li><strong>Clés à passe</strong> et organigrammes pour copropriétés, commerces et bureaux.</li></ul>"),
            ("Clés sécurisées : la carte de propriété",
             "<p>Les cylindres de sécurité sont livrés avec une <strong>carte de propriété</strong>. Elle est indispensable pour commander un double : c'est ce qui empêche qu'un tiers fasse copier vos clés à votre insu. Le double est alors commandé auprès du fabricant ou d'un distributeur agréé, avec un délai variable selon la marque.</p>"
             "<div class=\"callout info\">Vous avez perdu votre carte de propriété ? Il faut généralement changer le cylindre pour obtenir une nouvelle carte. Nous vous conseillons la solution la plus économique.</div>"),
            ("Combien de doubles faut-il ?",
             "<p>Gardez un double chez une personne de confiance (proche, voisin) : en cas de porte claquée, c'est la solution la plus économique. Évitez de cacher une clé près de la porte, et ne notez jamais votre adresse sur un porte-clés.</p>"),
        ],
        "faq": [
            ("Combien coûte un double de clé ?", "À partir de 15 € pour une clé standard. Les clés sécurisées sont plus chères et nécessitent la carte de propriété."),
            ("Puis-je faire reproduire une clé sécurisée sans la carte ?", "Non, c'est justement la protection apportée par la carte. Sans carte, il faut changer le cylindre."),
            ("Quel est le délai pour un double de clé ?", "Les clés standards sont reproduites rapidement. Les clés sécurisées sont commandées chez le fabricant, avec un délai variable selon la marque."),
        ],
        "combo_h1": "Reproduction de clés",
        "combo_title": "Double de clé {city} ({cp}) — reproduction dès 15 €",
        "combo_meta": "Reproduction de clés {a} : double de clé standard, clé sécurisée avec carte de propriété, clés à passe. Dès 15 €. ☎ 06 75 93 19 04",
        "combo_intros": [
            "Besoin d'un double de clé {a} ? Clés standards, sécurisées ou à passe : nous reproduisons vos clés sur place ou en atelier partenaire, à partir de 15 €.",
            "Reproduction de clés {a} : pour une clé sécurisée, munissez-vous de votre carte de propriété, nous nous occupons de la commande.",
            "Un double chez un proche reste la meilleure assurance contre la porte claquée. Nous reproduisons vos clés {a} rapidement.",
        ],
        "combo_points": [
            "Double de clé standard",
            "Clé sécurisée avec carte de propriété",
            "Clé de boîte aux lettres",
            "Clé de garage et de portail",
            "Clés à passe pour copropriété",
            "Organigramme de commerce",
        ],
        "combo_tip": "Pour une clé sécurisée, munissez-vous de votre carte de propriété : sans elle, aucun professionnel sérieux ne peut commander de double.",
    },
    # ------------------------------------------------------------------ CONNECTEE
    {
        "slug": "serrure-connectee-var",
        "image": "serrurier-devis-client.jpg",
        "image_alt": "Serrurier présentant une serrure à code à des clients",
        "combo": "serrure-connectee",
        "name": "Serrure connectée & électronique",
        "short": "Serrure connectée",
        "icon": "phone",
        "badge": "Sur devis",
        "price_label": "sur devis",
        "price_min": None,
        "title": "Serrure connectée dans le Var — installation et paramétrage",
        "meta": "Installation de serrure connectée, électronique, à code ou biométrique dans le Var : conseil, pose et paramétrage inclus. Devis gratuit. ☎ 06 75 93 19 04",
        "h1": "Serrure connectée et électronique dans le Var",
        "lead": "Serrure à code, à empreinte digitale ou pilotée depuis votre téléphone : nous vous conseillons, installons et <b>paramétrons votre serrure connectée</b>, avec une prise en main complète.",
        "checks": ["Conseil selon votre porte", "Paramétrage inclus", "Prise en main expliquée"],
        "card_desc": "Installation et paramétrage de serrures électroniques et biométriques, avec prise en main complète.",
        "card_checks": ["Paramétrage inclus", "Toutes marques"],
        "sections": [
            ("Pourquoi passer à une serrure connectée ?",
             "<ul><li><strong>Plus de clés à perdre</strong> : ouverture par code, empreinte, badge ou téléphone.</li>"
             "<li><strong>Accès à distance</strong> : ouvrir à un proche, un artisan ou un locataire de courte durée sans remettre de clé.</li>"
             "<li><strong>Historique des passages</strong> sur la plupart des modèles.</li>"
             "<li>Idéal pour les <strong>locations saisonnières</strong> et les <strong>résidences secondaires</strong>, nombreuses dans le Var.</li></ul>"),
            ("Bien choisir : les points à vérifier",
             "<p>Toutes les serrures connectées ne conviennent pas à toutes les portes. Nous vérifions avec vous la compatibilité avec votre porte et votre cylindre, le niveau de sécurité (certains modèles se posent sur un cylindre certifié), l'alimentation (piles, autonomie, alerte de batterie faible) et la solution de secours en cas de panne (clé mécanique, alimentation de dépannage).</p>"),
            ("Pose, paramétrage et prise en main",
             "<p>Nous installons la serrure, la paramétrons avec vous (codes, utilisateurs, application) et vous expliquons son fonctionnement. Vous repartez avec une serrure qui marche, et vous savez vous en servir.</p>"),
        ],
        "faq": [
            ("Une serrure connectée est-elle sûre ?", "Une serrure connectée de qualité, posée sur un cylindre de sécurité, offre un bon niveau de protection. Nous vous conseillons les modèles adaptés à votre porte."),
            ("Que se passe-t-il si les piles sont vides ?", "La plupart des modèles préviennent bien avant la fin des piles et prévoient une ouverture de secours (clé mécanique ou alimentation externe)."),
            ("Est-ce adapté à une location saisonnière ?", "Oui, c'est l'un des usages les plus intéressants : vous créez un code par séjour, sans remise de clés."),
        ],
        "combo_h1": "Serrure connectée et électronique",
        "combo_title": "Serrure connectée {city} — installation et paramétrage",
        "combo_meta": "Serrure connectée {a} : serrure à code, biométrique ou pilotée par téléphone, pose et paramétrage inclus. Devis gratuit. ☎ 06 75 93 19 04",
        "combo_intros": [
            "Envie d'ouvrir votre porte sans clé {a} ? Serrure à code, à empreinte ou pilotée par téléphone : nous installons et paramétrons votre serrure connectée.",
            "Location saisonnière ou résidence secondaire {a} : une serrure connectée vous permet de donner l'accès à distance, sans remise de clés.",
            "Nous vous conseillons {a} une serrure connectée compatible avec votre porte, la posons et vous expliquons son fonctionnement.",
        ],
        "combo_points": [
            "Serrure à code",
            "Serrure biométrique (empreinte)",
            "Serrure pilotée par smartphone",
            "Accès pour location saisonnière",
            "Contrôle d'accès de commerce",
            "Paramétrage et prise en main",
        ],
        "combo_tip": "Avant de commander une serrure connectée, prenez en photo votre porte côté intérieur et votre cylindre : nous vérifions la compatibilité avant tout achat.",
    },
    # ------------------------------------------------------------------ RIDEAU
    {
        "slug": "rideau-metallique-var",
        "image": "rideau-metallique.jpg",
        "image_alt": "Rideau métallique de commerce fermé",
        "combo": "rideau-metallique",
        "name": "Rideau métallique & volets",
        "short": "Volets métalliques",
        "icon": "wrench",
        "badge": "Dépannage",
        "price_label": "à partir de 79 €",
        "price_min": 79,
        "title": "Dépannage rideau métallique et volets dans le Var — dès 79 €",
        "meta": "Dépannage de rideau métallique, rideau de fer et volet roulant bloqué dans le Var, 7j/7 : diagnostic, réparation, serrure. Dès 79 €. ☎ 06 75 93 19 04",
        "h1": "Dépannage de rideau métallique et de volets dans le Var",
        "lead": "Rideau de fer bloqué, volet roulant qui ne remonte plus, serrure de rideau cassée : nous dépannons <b>commerces et particuliers</b>, 7j/7. Intervention à partir de 79 €.",
        "checks": ["Diagnostic sur place", "Pièces d'origine", "Commerces et particuliers"],
        "card_desc": "Réparation et dépannage de volets roulants et rideaux de fer bloqués ou déréglés.",
        "card_checks": ["Diagnostic gratuit", "Pièces d'origine"],
        "sections": [
            ("Nos interventions",
             "<ul><li><strong>Rideau métallique bloqué</strong> en position ouverte ou fermée.</li>"
             "<li><strong>Serrure de rideau</strong> cassée, grippée ou clé perdue.</li>"
             "<li><strong>Lames abîmées</strong> ou déformées après un choc ou une tentative d'effraction.</li>"
             "<li><strong>Problème de motorisation</strong> : moteur, télécommande, fins de course.</li>"
             "<li><strong>Volets roulants</strong> bloqués ou qui descendent de travers.</li></ul>"),
            ("Un commerce ne peut pas rester ouvert",
             "<p>Un rideau métallique bloqué en position ouverte empêche de fermer la boutique le soir ; bloqué fermé, il empêche d'ouvrir le matin. Nous intervenons rapidement pour <strong>remettre le rideau en service ou sécuriser le commerce</strong>, puis nous vous proposons une réparation durable avec un devis.</p>"),
            ("Entretien",
             "<p>Un rideau métallique s'entretient : graissage des coulisses, contrôle des ressorts ou du moteur, vérification de la serrure. Un entretien régulier évite les pannes au mauvais moment.</p>"),
        ],
        "faq": [
            ("Combien coûte le dépannage d'un rideau métallique ?", "À partir de 79 €. Le prix dépend de la panne et des pièces à remplacer ; il est annoncé avant intervention."),
            ("Intervenez-vous le week-end pour un commerce ?", "Oui, 7j/7. Un rideau bloqué ouvert est une urgence : nous faisons le nécessaire pour que vous puissiez fermer."),
            ("Réparez-vous aussi les volets roulants des particuliers ?", "Oui, nous dépannons les volets roulants bloqués ou déréglés."),
        ],
        "combo_h1": "Dépannage de rideau métallique et de volets",
        "combo_title": "Rideau métallique {city} ({cp}) — dépannage dès 79 €",
        "combo_meta": "Dépannage de rideau métallique et volet roulant {a}, 7j/7 : rideau bloqué, serrure, lames, moteur. Dès 79 €. {delay_txt}. ☎ 06 75 93 19 04",
        "combo_intros": [
            "Rideau de fer bloqué ou volet roulant en panne {a} ? Nous dépannons commerces et particuliers 7j/7, à partir de 79 €.",
            "Commerçant {a}, votre rideau métallique refuse de se fermer ? Nous intervenons rapidement pour sécuriser votre boutique, puis réparer durablement.",
            "Serrure de rideau cassée, lames abîmées, moteur en panne {a} : diagnostic sur place et prix annoncé avant réparation.",
        ],
        "combo_points": [
            "Rideau métallique bloqué",
            "Serrure de rideau cassée",
            "Lames abîmées",
            "Moteur et télécommande",
            "Volet roulant bloqué",
            "Entretien de rideau métallique",
        ],
        "combo_tip": "Si le rideau est bloqué à mi-hauteur, ne forcez pas à la main : un ressort ou un axe sous tension peut céder brutalement. Attendez notre arrivée.",
    },
]

# Page spéciale cambriolage / assurance (pas de déclinaison par commune)
ASSURANCE_PAGE = {
    "slug": "serrurier-cambriolage-assurance-var",
    "name": "Cambriolage & assurance",
    "image": "securisation-effraction.jpg",
    "image_alt": "Porte d'entrée forcée après une tentative d'effraction",
}

SERVICE_ICONS = {
    "bolt": '<path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>',
    "key": '<circle cx="8" cy="15" r="4" stroke="currentColor" stroke-width="1.7"/><path d="M11 12 20 3M16 7l3 3M14 9l2 2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    "lock": '<rect x="5" y="10" width="14" height="11" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.5" stroke="currentColor" stroke-width="1.7"/><path d="M10 6h4M12 18h.01" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.2 5.2L4 17l3 3 5.5-5.5a4 4 0 0 0 5.2-5.2l-2.4 2.4-2.6-.6-.6-2.6 2.6-2.2Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
    "shield": '<path d="M12 2 4 5v6c0 5 3.4 8.7 8 11 4.6-2.3 8-6 8-11V5l-8-3Z" stroke="currentColor" stroke-width="1.8"/><path d="M8.5 12l2.3 2.3L15.5 9.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
}
