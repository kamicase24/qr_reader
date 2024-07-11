from flask import render_template
from app.retails import bp
from app.extensions import Base, db
from sqlalchemy import func, case
from sqlalchemy.orm import Session




@bp.route('/ripley_chile/')
def ripley_chile():

    session = Session(db.engine)
    QueryInput = Base.classes.get('QueryInput')
    RipleyChileResult = Base.classes.get('RipleyChileResult')
    RipleyChileDelivery = Base.classes.get('RipleyChileDelivery')

    cross_table = session.query(
        QueryInput.id.label('QueryInput_id'),
        QueryInput.key_words_search.label('QueryInput_key_words_search'),
        RipleyChileResult.QueryInput_id.label('RipleyChileResult_QueryInput_id'),
        RipleyChileResult.id.label('RipleyChileResult_id'),
        RipleyChileResult.part_number.label('RipleyChileResult_part_number'),
        RipleyChileResult.name.label('RipleyChileResult_name'),
        RipleyChileResult.url.label('RipleyChileResult_url'),
        case(
            (RipleyChileResult.is_marketplace_product == 0, '1P'),
            else_='3P'
        ).label('RipleyChileResult_etq_seller'),
        RipleyChileResult.scrap_ini.label('RipleyChileResult_scrap_ini'),
        RipleyChileDelivery.value.label('RipleyChileDelivery_value'),
        func.min(RipleyChileDelivery.closest_date).label('RipleyChileDelivery_closest_date'),
        # RipleyChileDelivery.discount_delivery.label('RipleyChileDelivery_discount_delivery'),

        case(
            (RipleyChileDelivery.discount_delivery == None, 0.00),
            else_=RipleyChileDelivery.discount_delivery
        ).label('RipleyChileDelivery_discount_delivery'),

        case(
            (
                RipleyChileDelivery.value - case(
                    (RipleyChileDelivery.discount_delivery == None, 0.00),
                    else_=RipleyChileDelivery.discount_delivery
                ) < 0.00,
                0.00
            ),
            else_=RipleyChileDelivery.value - case(
                (RipleyChileDelivery.discount_delivery == None, 0.00),
                else_=RipleyChileDelivery.discount_delivery
            )
        ).label('RipleyChileDelivery_value_conFlete'),
        
    ).join(
        RipleyChileResult, QueryInput.id == RipleyChileResult.QueryInput_id
    ).join(
        RipleyChileDelivery, RipleyChileResult.id == RipleyChileDelivery.RipleyChileResult_id
    ).filter(
        func.date(QueryInput.created_at) == func.current_date(),
        func.date(RipleyChileResult.created_at) == func.current_date(),        
    ).group_by(
        QueryInput.id,
        QueryInput.key_words_search,
        RipleyChileResult.QueryInput_id,
        RipleyChileResult.id,
        RipleyChileResult.part_number,
        RipleyChileResult.name,
        RipleyChileResult.url,
        RipleyChileResult.is_marketplace_product,
        RipleyChileResult.scrap_ini,
        RipleyChileDelivery.value,
        RipleyChileDelivery.discount_delivery,
    ).all()

    session.close()
    return render_template('retails/ripley_chile.html', 
        cross_table=cross_table
    )