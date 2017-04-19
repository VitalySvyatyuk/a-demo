from referral.utils import set_agent_code


class AgentCodeMiddleware(object):
    """Processes agent codes, which are used on account creation.

    Agent code is used when calculating partner reports and profits.
    """

    def process_request(self, request):
        agent_code = request.GET.get('partner_id', request.GET.get('note'))

        if request.path.endswith(".css"):
            return

        try:
            agent_code = int(agent_code)
        except (ValueError, TypeError):
            return

        if agent_code > 2**32:
            return

        set_agent_code(request, agent_code)