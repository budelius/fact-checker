import type { KnowledgeRatingSummary, RatingRecord } from "../api/knowledge";

type RatingBadgeProps = {
  rating?: KnowledgeRatingSummary | RatingRecord | null;
};

export function RatingBadge({ rating }: RatingBadgeProps) {
  if (!rating) {
    return <span className="rating-badge rating-badge--insufficient">insufficient history</span>;
  }

  const modifier = rating.badge.replaceAll(" ", "-");
  return (
    <span className={`rating-badge rating-badge--${modifier}`}>
      {rating.badge}
      {rating.experimental ? <span>experimental</span> : null}
    </span>
  );
}
