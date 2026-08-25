import pytest
from datetime import datetime
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_ordem_servico import StatusOrdemServico


class TestOrdemServicoCreation:
    """Testes para criação e validação básica de Ordem de Serviço"""

    def test_criar_ordem_servico_com_dados_validos(self):
        """Deve criar uma ordem de serviço com dados válidos"""
        os = OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Troca de óleo e filtro"
        )

        assert os.id is None  # ID será preenchido pelo banco após salvar
        assert os.veiculo_id == "veiculo-123"
        assert str(os.descricao) == "Troca de óleo e filtro"
        assert os.status == StatusOrdemServico.RECEBIDA
        assert os.orcamento is None
        assert len(os.itens) == 0
        assert os.data_criacao is not None
        assert os.data_atualizacao is not None

    def test_criar_ordem_servico_com_orcamento(self):
        """Deve criar uma ordem de serviço com orçamento inicial"""
        os = OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Manutenção completa",
            orcamento=1500.00
        )

        assert os.orcamento == 1500.00

    def test_criar_ordem_servico_com_observacoes(self):
        """Deve criar uma ordem de serviço com observações"""
        obs = "Cliente solicitou entrega em 48 horas"
        os = OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Reparo de suspensão",
            observacoes=obs
        )

        assert os.observacoes == obs

    def test_falhar_ao_criar_sem_veiculo_id(self):
        """Deve falhar ao tentar criar sem veiculo_id"""
        with pytest.raises(ValueError, match="ID do veículo"):
            OrdemServico(veiculo_id="", descricao="Teste")

    def test_falhar_ao_criar_com_descricao_vazia(self):
        """Deve falhar ao tentar criar com descrição vazia"""
        with pytest.raises(ValueError, match="Descrição não pode ser vazia"):
            OrdemServico(veiculo_id="veiculo-123", descricao="")

    def test_falhar_ao_criar_com_descricao_muito_curta(self):
        """Deve falhar ao tentar criar com descrição muito curta"""
        with pytest.raises(ValueError, match="mínimo"):
            OrdemServico(veiculo_id="veiculo-123", descricao="AB")

    def test_falhar_ao_criar_com_descricao_muito_longa(self):
        """Deve falhar ao tentar criar com descrição muito longa"""
        descricao_longa = "A" * 1001
        with pytest.raises(ValueError, match="exceder"):
            OrdemServico(veiculo_id="veiculo-123", descricao=descricao_longa)


class TestAdicionarRemoverItens:
    """Testes para adição e remoção de itens (serviços) na OS"""

    @pytest.fixture
    def ordem_servico(self):
        return OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Manutenção do veículo"
        )

    def test_adicionar_item_valido(self, ordem_servico):
        """Deve adicionar um item válido à OS"""
        ordem_servico.adicionar_item("servico-1", 100.00, quantidade=1)

        assert len(ordem_servico.itens) == 1
        assert ordem_servico.itens[0]["servico_id"] == "servico-1"
        assert ordem_servico.itens[0]["valor"] == 100.00
        assert ordem_servico.itens[0]["quantidade"] == 1

    def test_adicionar_multiplos_itens(self, ordem_servico):
        """Deve adicionar múltiplos itens diferentes"""
        ordem_servico.adicionar_item("servico-1", 100.00)
        ordem_servico.adicionar_item("servico-2", 250.00, quantidade=2)
        ordem_servico.adicionar_item("servico-3", 75.50)

        assert len(ordem_servico.itens) == 3

    def test_falhar_ao_adicionar_mesmo_servico_duas_vezes(self, ordem_servico):
        """Não deve permitir adicionar o mesmo serviço duas vezes"""
        ordem_servico.adicionar_item("servico-1", 100.00)

        with pytest.raises(ValueError, match="já foi adicionado"):
            ordem_servico.adicionar_item("servico-1", 150.00)

    def test_falhar_ao_adicionar_item_com_quantidade_invalida(self, ordem_servico):
        """Não deve permitir quantidade menor ou igual a zero"""
        with pytest.raises(ValueError, match="maior que zero"):
            ordem_servico.adicionar_item("servico-1", 100.00, quantidade=0)

        with pytest.raises(ValueError, match="maior que zero"):
            ordem_servico.adicionar_item("servico-1", 100.00, quantidade=-5)

    def test_falhar_ao_adicionar_item_com_valor_negativo(self, ordem_servico):
        """Não deve permitir valor negativo"""
        with pytest.raises(ValueError, match="não pode ser negativo"):
            ordem_servico.adicionar_item("servico-1", -100.00)

    def test_remover_item_existente(self, ordem_servico):
        """Deve remover um item existente"""
        ordem_servico.adicionar_item("servico-1", 100.00)
        ordem_servico.adicionar_item("servico-2", 250.00)

        ordem_servico.remover_item("servico-1")

        assert len(ordem_servico.itens) == 1
        assert ordem_servico.itens[0]["servico_id"] == "servico-2"

    def test_falhar_ao_remover_item_inexistente(self, ordem_servico):
        """Não deve permitir remover serviço que não existe"""
        with pytest.raises(ValueError, match="não encontrado"):
            ordem_servico.remover_item("servico-inexistente")

    def test_falhar_ao_adicionar_item_sem_servico_id(self, ordem_servico):
        """Não deve permitir adicionar item sem o id do serviço"""
        with pytest.raises(ValueError, match="ID do serviço é obrigatório"):
            ordem_servico.adicionar_item("", 100.00)


class TestAdicionarRemoverInsumos:
    """Testes para adição e remoção de insumos avulsos na OS"""

    @pytest.fixture
    def ordem_servico(self):
        return OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Manutenção do veículo"
        )

    def test_adicionar_insumo_valido(self, ordem_servico):
        """Deve adicionar um insumo válido à OS"""
        ordem_servico.adicionar_insumo("insumo-1", 15.00, quantidade=2)

        assert len(ordem_servico.insumos_utilizados) == 1
        assert ordem_servico.insumos_utilizados[0]["insumo_id"] == "insumo-1"
        assert ordem_servico.insumos_utilizados[0]["valor"] == 15.00
        assert ordem_servico.insumos_utilizados[0]["quantidade"] == 2

    def test_adicionar_multiplos_insumos(self, ordem_servico):
        """Deve adicionar múltiplos insumos diferentes"""
        ordem_servico.adicionar_insumo("insumo-1", 10.00)
        ordem_servico.adicionar_insumo("insumo-2", 25.00, quantidade=3)

        assert len(ordem_servico.insumos_utilizados) == 2

    def test_falhar_ao_adicionar_mesmo_insumo_duas_vezes(self, ordem_servico):
        """Não deve permitir adicionar o mesmo insumo duas vezes"""
        ordem_servico.adicionar_insumo("insumo-1", 10.00)

        with pytest.raises(ValueError, match="já foi adicionado"):
            ordem_servico.adicionar_insumo("insumo-1", 12.00)

    def test_falhar_ao_adicionar_insumo_com_quantidade_invalida(self, ordem_servico):
        """Não deve permitir quantidade menor ou igual a zero"""
        with pytest.raises(ValueError, match="maior que zero"):
            ordem_servico.adicionar_insumo("insumo-1", 10.00, quantidade=0)

    def test_falhar_ao_adicionar_insumo_com_valor_negativo(self, ordem_servico):
        """Não deve permitir valor negativo"""
        with pytest.raises(ValueError, match="não pode ser negativo"):
            ordem_servico.adicionar_insumo("insumo-1", -10.00)

    def test_falhar_ao_adicionar_insumo_sem_id(self, ordem_servico):
        """Não deve permitir adicionar insumo sem o id"""
        with pytest.raises(ValueError, match="ID do insumo é obrigatório"):
            ordem_servico.adicionar_insumo("", 10.00)

    def test_remover_insumo_existente(self, ordem_servico):
        """Deve remover um insumo existente e devolver a quantidade removida"""
        ordem_servico.adicionar_insumo("insumo-1", 10.00, quantidade=4)
        ordem_servico.adicionar_insumo("insumo-2", 25.00)

        quantidade = ordem_servico.remover_insumo("insumo-1")

        assert quantidade == 4
        assert len(ordem_servico.insumos_utilizados) == 1
        assert ordem_servico.insumos_utilizados[0]["insumo_id"] == "insumo-2"

    def test_falhar_ao_remover_insumo_inexistente(self, ordem_servico):
        """Não deve permitir remover insumo que não existe"""
        with pytest.raises(ValueError, match="não encontrado"):
            ordem_servico.remover_insumo("insumo-inexistente")

    def test_orcamento_calculado_soma_servicos_e_insumos(self, ordem_servico):
        """O orçamento automático deve considerar serviços e insumos"""
        ordem_servico.adicionar_item("servico-1", 100.00, quantidade=1)
        ordem_servico.adicionar_insumo("insumo-1", 15.00, quantidade=2)

        assert ordem_servico.orcamento_calculado == 130.00


class TestEdicaoDeItensBloqueadaPorStatus:
    """Testes da trava que impede alterar serviços/insumos de uma OS já
    finalizada ou entregue"""

    @pytest.fixture
    def ordem_finalizada(self):
        ordem = OrdemServico(
            veiculo_id="veiculo-123", descricao="Manutenção do veículo"
        )
        ordem.adicionar_item("servico-1", 100.00)
        ordem.iniciar_diagnostico()
        ordem.enviar_para_aprovacao(orcamento=100.00)
        ordem.aprovar_e_iniciar_execucao()
        ordem.finalizar()
        return ordem

    @pytest.fixture
    def ordem_entregue(self, ordem_finalizada):
        ordem_finalizada.entregar()
        return ordem_finalizada

    @pytest.mark.parametrize("status_fixture", ["ordem_finalizada", "ordem_entregue"])
    def test_falhar_ao_adicionar_item(self, status_fixture, request):
        ordem = request.getfixturevalue(status_fixture)

        with pytest.raises(ValueError, match="Não é possível alterar"):
            ordem.adicionar_item("servico-2", 50.00)

    @pytest.mark.parametrize("status_fixture", ["ordem_finalizada", "ordem_entregue"])
    def test_falhar_ao_remover_item(self, status_fixture, request):
        ordem = request.getfixturevalue(status_fixture)

        with pytest.raises(ValueError, match="Não é possível alterar"):
            ordem.remover_item("servico-1")

    @pytest.mark.parametrize("status_fixture", ["ordem_finalizada", "ordem_entregue"])
    def test_falhar_ao_adicionar_insumo(self, status_fixture, request):
        ordem = request.getfixturevalue(status_fixture)

        with pytest.raises(ValueError, match="Não é possível alterar"):
            ordem.adicionar_insumo("insumo-1", 10.00)

    @pytest.mark.parametrize("status_fixture", ["ordem_finalizada", "ordem_entregue"])
    def test_falhar_ao_remover_insumo(self, status_fixture, request):
        ordem = request.getfixturevalue(status_fixture)
        # precisa existir um insumo para garantir que a trava de status é o
        # que barra, e não a validação de "insumo não encontrado"
        ordem.insumos_utilizados.append(
            {
                "insumo_id": "insumo-1",
                "valor": 10.00,
                "quantidade": 1,
                "data_adicionado": None,
            }
        )

        with pytest.raises(ValueError, match="Não é possível alterar"):
            ordem.remover_insumo("insumo-1")

    def test_adicionar_item_ainda_funciona_em_execucao(self):
        """A trava não pode bloquear status intermediários válidos"""
        ordem = OrdemServico(
            veiculo_id="veiculo-123", descricao="Manutenção do veículo"
        )
        ordem.adicionar_item("servico-1", 100.00)
        ordem.iniciar_diagnostico()
        ordem.enviar_para_aprovacao(orcamento=100.00)
        ordem.aprovar_e_iniciar_execucao()

        ordem.adicionar_item("servico-2", 50.00)

        assert len(ordem.itens) == 2


class TestTransicaoDeStatus:
    """Testes para transições de status da OS"""

    @pytest.fixture
    def ordem_servico(self):
        return OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Manutenção"
        )

    def test_fluxo_completo_de_status(self, ordem_servico):
        """Deve seguir o fluxo completo de status válido"""
        # Inicia como RECEBIDA
        assert ordem_servico.status == StatusOrdemServico.RECEBIDA

        # Passa para EM_DIAGNOSTICO
        ordem_servico.iniciar_diagnostico()
        assert ordem_servico.status == StatusOrdemServico.EM_DIAGNOSTICO

        # Passa para AGUARDANDO_APROVACAO
        ordem_servico.enviar_para_aprovacao(orcamento=1000.00)
        assert ordem_servico.status == StatusOrdemServico.AGUARDANDO_APROVACAO
        assert ordem_servico.orcamento == 1000.00

        # Volta para EM_DIAGNOSTICO (cliente não aprova)
        ordem_servico.retornar_para_diagnostico()
        assert ordem_servico.status == StatusOrdemServico.EM_DIAGNOSTICO

        # Volta para AGUARDANDO_APROVACAO
        ordem_servico.enviar_para_aprovacao(orcamento=950.00)
        assert ordem_servico.status == StatusOrdemServico.AGUARDANDO_APROVACAO

        # Aprova e inicia execução (com itens)
        ordem_servico.adicionar_item("servico-1", 500.00)
        ordem_servico.aprovar_e_iniciar_execucao()
        assert ordem_servico.status == StatusOrdemServico.EM_EXECUCAO

        # Finaliza
        ordem_servico.finalizar()
        assert ordem_servico.status == StatusOrdemServico.FINALIZADA

        # Entrega
        ordem_servico.entregar()
        assert ordem_servico.status == StatusOrdemServico.ENTREGUE

    def test_falhar_ao_transicionar_para_status_invalido(self, ordem_servico):
        """Não deve permitir transição inválida"""
        with pytest.raises(ValueError, match="Não é possível transicionar"):
            ordem_servico.enviar_para_aprovacao(1000.00)

    def test_enviar_para_aprovacao_sem_orcamento(self, ordem_servico):
        """Deve falhar ao enviar para aprovação sem orçamento positivo"""
        ordem_servico.iniciar_diagnostico()

        with pytest.raises(ValueError, match="positivo"):
            ordem_servico.enviar_para_aprovacao(orcamento=0)

        with pytest.raises(ValueError, match="positivo"):
            ordem_servico.enviar_para_aprovacao(orcamento=-100)

    def test_iniciar_execucao_sem_orcamento(self, ordem_servico):
        """Não deve iniciar execução sem orcamento definido"""
        ordem_servico.iniciar_diagnostico()
        ordem_servico.enviar_para_aprovacao(orcamento=1000.00)

        # Remove o orçamento
        ordem_servico.orcamento = None

        with pytest.raises(ValueError, match="Orçamento deve estar definido"):
            ordem_servico.aprovar_e_iniciar_execucao()

    def test_iniciar_execucao_sem_itens(self, ordem_servico):
        """Não deve iniciar execução sem itens (serviços)"""
        ordem_servico.iniciar_diagnostico()
        ordem_servico.enviar_para_aprovacao(orcamento=1000.00)

        with pytest.raises(ValueError, match="pelo menos um serviço"):
            ordem_servico.aprovar_e_iniciar_execucao()

    def test_registrar_mudanca_status_no_historico(self, ordem_servico):
        """Deve registrar cada mudança no histórico"""
        assert len(ordem_servico.historico_status) == 1  # Criação
        assert ordem_servico.historico_status[0]["status"] == StatusOrdemServico.RECEBIDA

        ordem_servico.iniciar_diagnostico()
        assert len(ordem_servico.historico_status) == 2
        assert ordem_servico.historico_status[1]["status"] == StatusOrdemServico.EM_DIAGNOSTICO
        assert ordem_servico.historico_status[1]["motivo"] == "Diagnóstico iniciado"

    def test_retornar_para_recebida(self, ordem_servico):
        """Deve retornar OS para status RECEBIDA para revisão completa"""
        ordem_servico.iniciar_diagnostico()
        ordem_servico.enviar_para_aprovacao(orcamento=1000.00)

        ordem_servico.retornar_para_recebida("Necessária revisão completa")

        assert ordem_servico.status == StatusOrdemServico.RECEBIDA
        assert len(ordem_servico.historico_status) == 4

    def test_enviar_para_aprovacao_com_observacoes(self, ordem_servico):
        """Deve atualizar as observações ao enviar para aprovação"""
        ordem_servico.iniciar_diagnostico()
        ordem_servico.enviar_para_aprovacao(
            orcamento=1000.00, observacoes="Aguardando peças"
        )

        assert ordem_servico.observacoes == "Aguardando peças"

    def test_finalizar_com_observacoes(self, ordem_servico):
        """Deve atualizar as observações ao finalizar"""
        ordem_servico.iniciar_diagnostico()
        ordem_servico.enviar_para_aprovacao(orcamento=1000.00)
        ordem_servico.adicionar_item("servico-1", 500.00)
        ordem_servico.aprovar_e_iniciar_execucao()

        ordem_servico.finalizar("Tudo concluído")

        assert ordem_servico.observacoes == "Tudo concluído"

    def test_entregar_com_observacoes(self, ordem_servico):
        """Deve atualizar as observações ao entregar"""
        ordem_servico.iniciar_diagnostico()
        ordem_servico.enviar_para_aprovacao(orcamento=1000.00)
        ordem_servico.adicionar_item("servico-1", 500.00)
        ordem_servico.aprovar_e_iniciar_execucao()
        ordem_servico.finalizar()

        ordem_servico.entregar("Cliente satisfeito")

        assert ordem_servico.observacoes == "Cliente satisfeito"

    def test_falhar_ao_retornar_para_diagnostico_de_status_invalido(
        self, ordem_servico
    ):
        """Não deve permitir retornar para diagnóstico fora de aguardando aprovação"""
        with pytest.raises(ValueError, match="Não é possível retornar"):
            ordem_servico.retornar_para_diagnostico()

    def test_falhar_ao_retornar_para_recebida_de_status_invalido(
        self, ordem_servico
    ):
        """Não deve permitir retornar para recebida a partir de estado final"""
        ordem_servico.iniciar_diagnostico()
        ordem_servico.enviar_para_aprovacao(orcamento=1000.00)
        ordem_servico.adicionar_item("servico-1", 500.00)
        ordem_servico.aprovar_e_iniciar_execucao()

        with pytest.raises(ValueError, match="Não é possível retornar"):
            ordem_servico.retornar_para_recebida()


class TestComportamentosOrdemServico:
    """Testes para comportamentos específicos da OS"""

    @pytest.fixture
    def ordem_servico(self):
        return OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Manutenção completa"
        )

    def test_pode_ser_finalizada(self, ordem_servico):
        """Deve verificar se OS pode ser finalizada"""
        # Não pode ser finalizada em RECEBIDA
        assert not ordem_servico.pode_ser_finalizada()

        # Não pode ser finalizada em EM_DIAGNOSTICO
        ordem_servico.iniciar_diagnostico()
        assert not ordem_servico.pode_ser_finalizada()

        # Não pode ser finalizada sem itens mesmo em EM_EXECUCAO
        ordem_servico.enviar_para_aprovacao(1000.00)
        
        # Precisamos adicionar item antes de aprovar
        ordem_servico.adicionar_item("servico-1", 500.00)
        ordem_servico.aprovar_e_iniciar_execucao()
        
        # Agora pode ser finalizada
        assert ordem_servico.pode_ser_finalizada()

    def test_obter_resumo(self, ordem_servico):
        """Deve retornar um resumo das informações"""
        ordem_servico.adicionar_item("servico-1", 100.00)
        ordem_servico.adicionar_item("servico-2", 200.00)

        resumo = ordem_servico.obter_resumo()

        assert resumo["id"] == ordem_servico.id
        assert resumo["veiculo_id"] == "veiculo-123"
        assert resumo["quantidade_servicos"] == 2
        assert resumo["status"] == "Recebida"
        assert "status_descricao" in resumo

    def test_atualizar_timestamp_ao_adicionar_item(self, ordem_servico):
        """Deve atualizar timestamp ao modificar OS"""
        data_inicial = ordem_servico.data_atualizacao

        import time
        time.sleep(0.01)  # Pequeno atraso

        ordem_servico.adicionar_item("servico-1", 100.00)

        assert ordem_servico.data_atualizacao > data_inicial

    def test_adicionar_observacoes_durante_diagnostico(self, ordem_servico):
        """Deve permitir adicionar observações durante o diagnóstico"""
        obs_inicial = ordem_servico.observacoes

        ordem_servico.iniciar_diagnostico("Necessário substituir peça X")

        assert ordem_servico.observacoes == "Necessário substituir peça X"

    def test_status_enum_transicoes_validas(self):
        """Deve retornar transições válidas corretamente"""
        transicoes_recebida = StatusOrdemServico.get_transicoes_validas(
            StatusOrdemServico.RECEBIDA
        )
        assert StatusOrdemServico.EM_DIAGNOSTICO in transicoes_recebida
        assert len(transicoes_recebida) == 1

        transicoes_em_diagnostico = StatusOrdemServico.get_transicoes_validas(
            StatusOrdemServico.EM_DIAGNOSTICO
        )
        assert StatusOrdemServico.AGUARDANDO_APROVACAO in transicoes_em_diagnostico
        assert StatusOrdemServico.RECEBIDA in transicoes_em_diagnostico

        transicoes_aguardando = StatusOrdemServico.get_transicoes_validas(
            StatusOrdemServico.AGUARDANDO_APROVACAO
        )
        assert StatusOrdemServico.EM_EXECUCAO in transicoes_aguardando
        # Transição exposta por retornar_para_diagnostico — precisa constar no grafo
        assert StatusOrdemServico.EM_DIAGNOSTICO in transicoes_aguardando
        assert StatusOrdemServico.RECEBIDA in transicoes_aguardando

        transicoes_entregue = StatusOrdemServico.get_transicoes_validas(
            StatusOrdemServico.ENTREGUE
        )
        assert len(transicoes_entregue) == 0  # Sem transições possíveis

    def test_descrever_status(self):
        """Deve retornar descrição legível para cada status"""
        descricao = StatusOrdemServico.descrever_status(StatusOrdemServico.RECEBIDA)
        assert "Ordem recebida" in descricao

        descricao = StatusOrdemServico.descrever_status(StatusOrdemServico.EM_EXECUCAO)
        assert "Serviços em execução" in descricao


class TestOrcamentoAutomatico:
    """Testes do orçamento gerado automaticamente a partir dos itens da OS"""

    @pytest.fixture
    def ordem_servico(self):
        return OrdemServico(
            veiculo_id="veiculo-123",
            descricao="Manutenção do veículo"
        )

    def test_orcamento_calculado_soma_valor_vezes_quantidade(self, ordem_servico):
        """Deve somar valor unitário × quantidade de cada serviço"""
        ordem_servico.adicionar_item("servico-1", 100.00, quantidade=2)
        ordem_servico.adicionar_item("servico-2", 75.50, quantidade=1)

        assert ordem_servico.orcamento_calculado == 275.50

    def test_orcamento_calculado_e_zero_sem_itens(self, ordem_servico):
        """Sem serviços adicionados, o total calculado é zero"""
        assert ordem_servico.orcamento_calculado == 0

    def test_orcamento_calculado_arredonda_para_duas_casas(self, ordem_servico):
        """Deve arredondar para 2 casas, evitando ruído de ponto flutuante"""
        ordem_servico.adicionar_item("servico-1", 0.1, quantidade=3)

        assert ordem_servico.orcamento_calculado == 0.30

    def test_envia_para_aprovacao_gerando_orcamento_automaticamente(
        self, ordem_servico
    ):
        """Sem orçamento informado, usa o total calculado dos serviços"""
        ordem_servico.adicionar_item("servico-1", 120.00, quantidade=2)
        ordem_servico.adicionar_item("servico-2", 60.00)
        ordem_servico.iniciar_diagnostico()

        ordem_servico.enviar_para_aprovacao()

        assert ordem_servico.status == StatusOrdemServico.AGUARDANDO_APROVACAO
        assert ordem_servico.orcamento == 300.00

    def test_orcamento_manual_prevalece_sobre_o_calculado(self, ordem_servico):
        """Valor informado manualmente permite desconto sobre o total"""
        ordem_servico.adicionar_item("servico-1", 100.00, quantidade=2)
        ordem_servico.iniciar_diagnostico()

        ordem_servico.enviar_para_aprovacao(orcamento=180.00)

        assert ordem_servico.orcamento == 180.00
        assert ordem_servico.orcamento_calculado == 200.00

    def test_falha_ao_gerar_orcamento_automatico_sem_itens(self, ordem_servico):
        """Sem serviços não há o que orçar — erro deve explicar isso"""
        ordem_servico.iniciar_diagnostico()

        with pytest.raises(ValueError, match="não possui serviços adicionados"):
            ordem_servico.enviar_para_aprovacao()

    def test_orcamento_negativo_e_rejeitado_na_criacao(self):
        """A OS não pode nascer com orçamento negativo"""
        with pytest.raises(ValueError, match="positivo"):
            OrdemServico(
                veiculo_id="veiculo-123",
                descricao="Manutenção",
                orcamento=-500.00,
            )

    def test_orcamento_invalido_e_rejeitado_na_criacao(self):
        """Valor não numérico de orçamento é rejeitado"""
        with pytest.raises(ValueError, match="número válido"):
            OrdemServico(
                veiculo_id="veiculo-123",
                descricao="Manutenção",
                orcamento="abc",
            )

    def test_resumo_expoe_orcamento_calculado(self, ordem_servico):
        """O resumo deve mostrar o total calculado ao lado do aprovado"""
        ordem_servico.adicionar_item("servico-1", 100.00, quantidade=2)

        resumo = ordem_servico.obter_resumo()

        assert resumo["orcamento_calculado"] == 200.00
        assert resumo["orcamento"] is None
